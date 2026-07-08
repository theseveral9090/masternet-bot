# MasterNet APK

## Como compilar o APK

### Metodo 1: Usando o Buildozer
1. Instale o Buildozer: `pip install buildozer`
2. Navegue ate a pasta `apk/`: `cd apk`
3. Execute: `buildozer android debug`
4. O APK sera gerado em `bin/` (e.g., `bin/masternet-1.0-arm64-v8a-debug.apk`)
5. Transfira para o celular e instale

### Metodo 2: Usando Google Colab
1. https://colab.research.google.com
2. Rode:

```
!pip install buildozer
!git clone https://github.com/SEU_USUARIO/masternet-bot
%cd masternet-bot/apk
!buildozer android debug
```

3. Baixe o APK de `apk/bin/`

### Metodo 3: PWA (sem APK)
1. Abra este link no Chrome do celular:
2. Toque em "Adicionar a tela inicial"
3. Funciona como app sem precisar compilar nada
