#include <WiFi.h>
#include <time.h>
#include <HTTPClient.h>

#define PIN_SCT013 1
#define PIN_LM358  2

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverUrl = "http://YOUR_IP:8000/rt_energy/upload/";
#define WIFI_CHANNEL 6

//Sincronizacao com a hora atual (-3 é o horário de Brasília)
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = -3 * 3600;
const int   daylightOffset_sec = 0;

//Tamanho do buffer limita quantidade de amostras (1s / 8ms = 125 amostras (125Hz))
#define BUFFER_SIZE 500

short int bufferCore0[BUFFER_SIZE];
short int bufferCore1[BUFFER_SIZE];
short int indexCore0 = 0;
short int indexCore1 = 0;

portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
EventGroupHandle_t syncGroup;
#define BIT_START  BIT0
#define BIT_STOP   BIT1

void setupTime() {
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.print("Sincronizando hora via NTP");
  time_t now = time(nullptr);
  while (now < 8 * 3600 * 2) {
    delay(500);
    Serial.print(".");
    now = time(nullptr);
  }
  Serial.println();
  struct tm timeinfo;
  localtime_r(&now, &timeinfo);
  Serial.printf("Hora sincronizada: %02d:%02d:%02d\n", timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);
}

String getISO8601Timestamp() {
  struct timeval tv;
  gettimeofday(&tv, nullptr);  // Pega segundos + micros

  struct tm timeinfo;
  gmtime_r(&tv.tv_sec, &timeinfo);  // UTC

  char buffer[40];
  int millisec = tv.tv_usec / 1000;

  snprintf(
    buffer, sizeof(buffer),
    "%04d-%02d-%02dT%02d:%02d:%02d.%03dZ",
    timeinfo.tm_year + 1900,
    timeinfo.tm_mon + 1,
    timeinfo.tm_mday,
    timeinfo.tm_hour,
    timeinfo.tm_min,
    timeinfo.tm_sec,
    millisec
  );

  return String(buffer);
}

void taskCore0(void* parameter) {
  for (;;) {
    xEventGroupWaitBits(syncGroup, BIT_START, false, true, portMAX_DELAY);

    if (indexCore0 < BUFFER_SIZE) {
      //Descomentar para enviar dados reais
      int lm358_raw = analogRead(PIN_LM358);
      portENTER_CRITICAL(&mux);
      //Descomentar para enviar dados reais
      bufferCore0[indexCore0] = lm358_raw;
      //Simulando dados mocados
      //bufferCore0[indexCore0].value = random(0, 30);
      indexCore0++;
      portEXIT_CRITICAL(&mux);
    }

    //Delay de 5ms
    vTaskDelay(pdMS_TO_TICKS(5));
  }
}

void taskCore1(void* parameter) {
  for (;;) {
    xEventGroupWaitBits(syncGroup, BIT_START, false, true, portMAX_DELAY);

    if (indexCore1 < BUFFER_SIZE) {
      //Descomentar para enviar dados reais
      int sct013_raw = analogRead(PIN_SCT013);
      portENTER_CRITICAL(&mux);
      //Descomentar para enviar dados reais
      bufferCore1[indexCore1] = sct013_raw;
      //Simulando dados mocados
      //bufferCore1[indexCore1].value = random(0, 30);
      indexCore1++;
      portEXIT_CRITICAL(&mux);
    }

    //Delay de 5ms
    vTaskDelay(pdMS_TO_TICKS(5));
  }
}

void taskOrquestrador(void* parameter) {
  for (;;) {
    indexCore0 = 0;
    indexCore1 = 0;
    xEventGroupClearBits(syncGroup, BIT_STOP);
    xEventGroupSetBits(syncGroup, BIT_START);

    //Espera medições (4 segundos)
    vTaskDelay(pdMS_TO_TICKS(4000));

    //Desabilita medições
    xEventGroupClearBits(syncGroup, BIT_START);
    xEventGroupSetBits(syncGroup, BIT_STOP);

    //Monta o JSON
    String finalTimestamp = getISO8601Timestamp();
    String payload = "{";

    // Adiciona o timestamp final em ISO 8601 (UTC), ex: "2025-07-27T17:25:30.123Z"
    payload += "\"timestamp\":\"" + finalTimestamp + "\",";

    // Lista de valores do core0
    payload += "\"lm358\":[";
    for (int i = 0; i < indexCore0; ++i) {
      payload += String(bufferCore0[i]);
      if (i < indexCore0 - 1) payload += ",";
    }
    payload += "],";

    // Lista de valores do core1
    payload += "\"sct013\":[";
    for (int i = 0; i < indexCore1; ++i) {
      payload += String(bufferCore1[i]);
      if (i < indexCore1 - 1) payload += ",";
    }
    payload += "]";

    payload += "}";

    //TESTE
    //Serial.println(payload);

    //Envio HTTP para servidor externo
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");
      int httpResponseCode = http.POST(payload);
      if (httpResponseCode > 0) {
        Serial.printf("[HTTP] Sucesso: %d\n", httpResponseCode);
      } else {
        Serial.printf("[HTTP] Erro: %s\n", http.errorToString(httpResponseCode).c_str());
      }
      http.end();
    } else {
      Serial.println("WiFi desconectado.");
    }
  }

  //Assim que ele termina o envio, ele já retoma a medição (envio toma somente o tempo necessario)
}

void setup() {
  Serial.begin(115200);

  //Conexao WiFi
  WiFi.begin(ssid, password, WIFI_CHANNEL);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");
  Serial.println(WiFi.localIP());

  //Sincronização de tempo
  setupTime();

  syncGroup = xEventGroupCreate();

  //Cada task fica fixa em um core (core 1 é dividido entre medicao e envio, mas implementacao evita preempcao e concorrencia)
  xTaskCreatePinnedToCore(taskCore0, "Core0Task", 2048, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(taskCore1, "Core1Task", 2048, NULL, 1, NULL, 1);
  xTaskCreatePinnedToCore(taskOrquestrador, "Orquestrador", 4096, NULL, 1, NULL, 1);
}

void loop() {
}

