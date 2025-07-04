/*
Nessa abordagem, o ESP32 preenche dois vetores de 120 elementos cada (60Hz * 2, pelo Teorema da Amostragem), com tempo de preenchimento de 8 ms (1/120).
Cada vetor é preenchido em um núcleo e, a cada 1 segundo, quando o vetor é preenchido totalmente, ele realiza o envio desses vetores no segundo seguinte. 
Ou seja, há um intervalo de 1 segundo na medição, mas o ESP32 fica dedicado à tarefa de envio nesse tempo.
A medição está representada no códigopela geração de números aleatórios. Deve-se substituir essa geração pela leitura analógica dos sensores e conversão ADC.
*/

#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "SEU_SSID";
const char* password = "SUA_SENHA";

WebServer server(80);

const int vetorSize = 120;

float vetorCore0[vetorSize];
float vetorCore1[vetorSize];

volatile bool gerarVetores = true;  // Flag para controlar geração/espera

portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

void taskCore0(void* parameter) {
  while (true) {
    if (gerarVetores) {
      for (int i = 0; i < vetorSize; i++) {
        float valor = random(0, 1000) / 10.0;

        portENTER_CRITICAL(&mux);
        vetorCore0[i] = valor;
        portEXIT_CRITICAL(&mux);

        delay(8);  // Aprox 8ms * 120 = ~1s para gerar todo vetor
      }
    } else {
      vTaskDelay(pdMS_TO_TICKS(100));  // Espera 100ms antes de checar novamente
    }
  }
}

void taskCore1(void* parameter) {
  while (true) {
    if (gerarVetores) {
      for (int i = 0; i < vetorSize; i++) {
        float valor = random(0, 1000) / 10.0;

        portENTER_CRITICAL(&mux);
        vetorCore1[i] = valor;
        portEXIT_CRITICAL(&mux);

        delay(8);
      }
    } else {
      vTaskDelay(pdMS_TO_TICKS(100));
    }
  }
}

void handleVetores() {
  // Só responde quando vetor estiver pronto (geração completa)
  // Se estiver gerando, pode responder com aviso ou último vetor

  String json = "{";

  portENTER_CRITICAL(&mux);
  // Vetor Core 0
  json += "\"core0\":[";
  for (int i = 0; i < vetorSize; i++) {
    json += String(vetorCore0[i], 1);
    if (i < vetorSize - 1) json += ",";
  }
  json += "],";

  // Vetor Core 1
  json += "\"core1\":[";
  for (int i = 0; i < vetorSize; i++) {
    json += String(vetorCore1[i], 1);
    if (i < vetorSize - 1) json += ",";
  }
  json += "]";
  portEXIT_CRITICAL(&mux);

  json += "}";

  server.send(200, "application/json", json);
}

void controleGeracao() {
  // Controla o ciclo 1s gerar + 1s enviar
  while (true) {
    gerarVetores = true;   // Começa gerando
    vTaskDelay(pdMS_TO_TICKS(1000));

    gerarVetores = false;  // Para gerar, entra na fase de envio
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));

  WiFi.begin(ssid, password);
  Serial.print("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  server.on("/vetores", handleVetores);
  server.begin();

  xTaskCreatePinnedToCore(taskCore0, "GerarCore0", 4096, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(taskCore1, "GerarCore1", 4096, NULL, 1, NULL, 1);

  xTaskCreate([](void*){
    controleGeracao();
  }, "ControleGeracao", 2048, NULL, 1, NULL);

}

void loop() {
  server.handleClient();
}

