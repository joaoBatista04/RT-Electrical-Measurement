#include <WiFi.h>
#include <time.h>

#define PIN_SCT013 1
#define PIN_LM358  2

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverUrl = "http://localhost:5000/data";
#define WIFI_CHANNEL 6

//Sincronizacao com a hora atual (-3 é o horário de Brasília)
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = -3 * 3600;
const int   daylightOffset_sec = 0;

//Tamanho do buffer esta 200 amostras (1s / 5ms = 200 amostras)
#define BUFFER_SIZE 200

struct Sample {
  time_t timestamp;  //Timestamp em segundos Unix Epoch
  float value;
};

Sample bufferCore0[BUFFER_SIZE];
Sample bufferCore1[BUFFER_SIZE];
int indexCore0 = 0;
int indexCore1 = 0;

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

void taskCore0(void* parameter) {
  for (;;) {
    xEventGroupWaitBits(syncGroup, BIT_START, false, true, portMAX_DELAY);

    if (indexCore0 < BUFFER_SIZE) {
      //Descomentar para enviar dados reais
      //int lm358_raw = analogRead(PIN_LM358);
      time_t ts = time(nullptr);
      portENTER_CRITICAL(&mux);
      bufferCore0[indexCore0].timestamp = ts;
      //Descomentar para enviar dados reais
      //bufferCore0[indexCore0].value = lm358_raw;
      //Simulando dados mocados
      bufferCore0[indexCore0].value = random(0, 30);
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
      //int sct013_raw = analogRead(PIN_SCT013);
      time_t ts = time(nullptr);
      portENTER_CRITICAL(&mux);
      bufferCore1[indexCore1].timestamp = ts;
      //Descomentar para enviar dados reais
      //bufferCore1[indexCore1].value = sct013_raw;
      //Simulando dados mocados
      bufferCore1[indexCore1].value = random(0, 30);
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

    //Espera medições
    vTaskDelay(pdMS_TO_TICKS(1000));

    //Desabilita medições
    xEventGroupClearBits(syncGroup, BIT_START);
    xEventGroupSetBits(syncGroup, BIT_STOP);

    //Monta o JSON
    String payload = "{";
    payload += "\"tensao\": [";
    for (int i = 0; i < indexCore0; ++i) {
      payload += "{\"timestamp\":" + String(bufferCore0[i].timestamp) + ",\"value\":" + String(bufferCore0[i].value, 1) + "}";
      if (i < indexCore0 - 1) payload += ",";
    }
    payload += "],\"corrente\": [";
    for (int i = 0; i < indexCore1; ++i) {
      payload += "{\"timestamp\":" + String(bufferCore1[i].timestamp) + ",\"value\":" + String(bufferCore1[i].value, 1) + "}";
      if (i < indexCore1 - 1) payload += ",";
    }
    payload += "]}";

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

