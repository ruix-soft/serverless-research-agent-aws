# 6. CI/CD Enterprise con GitHub Actions y Autenticación OIDC (Zero Static Secrets)

* **Estatus:** Aceptado
* **Fecha:** 2026-08-24

## Contexto

Para evolucionar el proyecto hacia estándares de nivel producción y DevSecOps, se requería automatizar las fases de integración (pruebas unitarias, análisis estático, linting y validación de infraestructura) y despliegue continuo (CD) a AWS.

El enfoque tradicional en pipelines de CI/CD consiste en generar credenciales IAM de larga duración (`AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`) y almacenarlas en los secretos de GitHub. Este enfoque introduce riesgos de seguridad críticos:
1. **Riesgo de Fuga de Credenciales:** Las claves estáticas son susceptibles a exfiltración, logs accidentales o accesos no autorizados si el repositorio se ve comprometido.
2. **Falta de Rotación Automática:** Las claves permanentes requieren procedimientos manuales o scripts de rotación periódica.
3. **Violación del Principio de Mínimo Privilegio:** Muchas veces se asignan permisos amplios a las claves estáticas para evitar fallos en el pipeline.

## Decisión

Adoptar la metodología de arquitectura y seguridad de **Luis Ruiz** implementando un pipeline de **CI/CD Enterprise con GitHub Actions y OpenID Connect (OIDC)**:

1. **Autenticación sin Claves Estáticas (Zero Static Secrets via OIDC):**
   - Se configura un Proveedor de Identidad OIDC (`token.actions.githubusercontent.com`) en AWS IAM.
   - GitHub Actions solicita un token web JSON (JWT) firmado criptográficamente por GitHub en cada ejecución de trabajo.
   - Mediante la acción `aws-actions/configure-aws-credentials@v4`, GitHub Actions asume el rol `GitHubActionsServerlessResearchAgentDeployRole` mediante la API `sts:AssumeRoleWithWebIdentity`.
   - La política de confianza del rol restringe estrictamente la asunción al repositorio `ruix-soft/serverless-research-agent-aws`.
   - Las credenciales devueltas por AWS STS son efímeras (validez de 1 hora) y se destruyen al finalizar el job.

2. **Pipeline Multi-Etapa Automatizado (`.github/workflows/pipeline.yml`):**
   - **Etapa 1 (`lint-and-test`):** Configura Python 3.12, instala dependencias con caché y ejecuta `flake8` junto a la suite completa de 114 pruebas unitarias de `pytest` con cobertura.
   - **Etapa 2 (`sam-validation`):** Valida la sintaxis y buenas prácticas del template SAM con `sam validate --lint`.
   - **Etapa 3 (`deploy`):** Se ejecuta condicionalmente en la rama `main` tras el éxito de las etapas anteriores, compilando con `sam build` y desplegando automáticamente en AWS CloudFormation (`sam deploy`).

3. **Infraestructura como Código para OIDC (`infrastructure/github-oidc-role.yaml`):**
   - Plantilla CloudFormation independiente para aprovisionar el proveedor OIDC y el rol de despliegue con políticas IAM de mínimo privilegio sobre CloudFormation, S3, Lambda, DynamoDB, Step Functions, API Gateway e IAM PassRole.

## Consecuencias

* **Positivas:**
  * **Seguridad de Nivel Empresarial:** Eliminación del 100% de secretos estáticos y contraseñas de AWS en GitHub.
  * **Trazabilidad y Auditoría en AWS CloudTrail:** Todas las acciones ejecutadas por el pipeline quedan registradas con la identidad del commit y del workflow de GitHub Actions.
  * **Garantía de Calidad Continua:** Ningún código llega a producción en AWS si no supera las 114 pruebas unitarias y las validaciones de linting y SAM.
  * **Facilidad de Mantenimiento:** El rol de despliegue se gestiona como código en el mismo repositorio.
* **Negativas:**
  * Se requiere el aprovisionamiento inicial del rol OIDC en la cuenta de AWS antes de la primera ejecución del pipeline.

