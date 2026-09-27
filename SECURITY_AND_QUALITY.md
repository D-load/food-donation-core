# Seguridad y calidad del proyecto

## 1) Seguridad con OWASP ZAP

Se recomienda ejecutar el siguiente comando para validar el servicio en entorno de prueba:

```bash
docker run --rm -v "$(pwd):/zap/wrk/:rw" \
  owasp/zap2docker-stable:latest \
  zap-baseline.py -t http://127.0.0.1:8000 -g gen.conf -r zap-report.html
```

### Qué detecta
- XSS (Cross-Site Scripting)
- Inyecciones SQL (SQLi)
- Headers inseguros
- Fugas de información
- Configuraciones HTTP débiles

### Criterio de aceptación
- El análisis debe devolver una clasificación de riesgo clara.
- Si existen alertas medias o altas, deben documentarse y corregirse antes del despliegue productivo.

## 2) Calidad con SonarQube

Se configura el archivo `sonar-project.properties` para analizar:
- código fuente en `app/`
- pruebas en `tests/`
- cobertura desde `coverage.xml`

### Métricas clave a revisar
- deuda técnica
- code smells
- duplicación
- cobertura de pruebas
- vulnerabilidades y bugs

### Ejemplo de ejecución local

```bash
sonar-scanner \
  -Dsonar.projectKey=food-donations-core \
  -Dsonar.sources=app \
  -Dsonar.tests=tests \
  -Dsonar.python.coverage.reportPaths=coverage.xml \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=<TOKEN>
```

## 3) Métricas esperadas del proyecto actual

Con la validación ejecutada en esta sesión, el proyecto reporta:

- 7 pruebas pasando
- Cobertura total: 97.59%
- Umbral de cobertura requerido: 80%

Esto indica que el proyecto está en una buena línea de calidad para continuar con despliegues a entorno de prueba.
