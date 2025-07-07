/*
Nessa abordagem, duas medições estão sendo feitas individualmente em cada núcleo do ESP32. Toda vez que há uma requisição HTTP, o núcleo 2 passa a dividir a medição com o envio de dados
(o que pode prejudicar a medição feita nesse núcleo), com o gerenciamento de uso de CPU sendo feita pelo FreeRTOS. No código, a medição está representada pela geração de números aleatórios,
que pode ser substituída pela leitura analógica e conversão ADC.
*/

#include <WiFi.h>
#include <WebServer.h>

#define PIN_SCT013 1  // GPIO1 para SCT-013
#define PIN_LM358  2  // GPIO2 para saída do LM358

const char* ssid = "YOUR_SSID";  // Substitua pelo seu SSID
const char* password = "YOUR_PASSWORD";  // Substitua pela sua senha

WebServer server(80);

float valorCore0 = 0.0;
float valorCore1 = 0.0;

// Mutex
portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

void taskCore0(void* parameter) {
  for (;;) {
    int lm358_raw  = analogRead(PIN_LM358);

    portENTER_CRITICAL(&mux);
    valorCore0 = lm358_raw;
    //valorCore0 = ((lm358_raw / 4095.0) * 500) - 250;
    portEXIT_CRITICAL(&mux);

    vTaskDelay(pdMS_TO_TICKS(10));  // Atualização a cada 100 milisegundos
  }
}

void taskCore1(void* parameter) {
  for (;;) {
    int sct013_raw = analogRead(PIN_SCT013);

    portENTER_CRITICAL(&mux);
    valorCore1 = sct013_raw;
    //valorCore1 = ((sct013_raw / 4095.0) * 200) - 100;
    portEXIT_CRITICAL(&mux);

    vTaskDelay(pdMS_TO_TICKS(10));  // Atualização a cada 100 milisegundos
  }
}

void handleValores() {
  float v0, v1;

  portENTER_CRITICAL(&mux);
  v0 = valorCore0;
  v1 = valorCore1;
  portEXIT_CRITICAL(&mux);

  String resposta = "{";
  resposta += "\"core0\": [" + String(v0, 1) + "],";
  resposta += "\"core1\": [" + String(v1, 1);
  resposta += "]}";

  server.send(200, "application/json", resposta);
}

void handleRMS() {
  float v0, v1;
  // portENTER_CRITICAL(&mux);
  // v0 = valorCore0;
  // v1 = valorCore1;
  // portEXIT_CRITICAL(&mux);

  // String resposta = "{";
  // resposta += "\"core0\": [" + String(v0, 1) + "],";
  // resposta += "\"core1\": [" + String(v1, 1);
  // resposta += "]}";

  // server.send(200, "application/json", resposta);
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());

  server.on("/valores", handleValores);
  server.on("/rms", handleRMS);
  server.begin();

  xTaskCreatePinnedToCore(taskCore0, "Core0Task", 2048, NULL, 1, NULL, 0);  // Core 0
  xTaskCreatePinnedToCore(taskCore1, "Core1Task", 2048, NULL, 1, NULL, 1);  // Core 1
}

void loop() {
  server.handleClient();
}