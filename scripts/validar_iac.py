"""Valida el manifiesto IaC: YAML válido, zona horaria y umbral versionados, buenas prácticas básicas."""
import sys

import yaml

docs = list(yaml.safe_load_all(open("infra/sala02.k8s.yaml", encoding="utf-8")))
errores = []
kinds = {d["kind"]: d for d in docs}
cfg = kinds.get("ConfigMap", {}).get("data", {})
if cfg.get("TZ_SEDE") != "America/Lima":
    errores.append("TZ_SEDE debe ser America/Lima")
if float(cfg.get("UMBRAL_LUX", 0)) != 300:
    errores.append("UMBRAL_LUX debe ser 300")
cont = kinds["Deployment"]["spec"]["template"]["spec"]["containers"][0]
if not cont.get("securityContext", {}).get("runAsNonRoot"):
    errores.append("el contenedor debe correr como no-root")
if "readinessProbe" not in cont:
    errores.append("falta readinessProbe")
if errores:
    print("IaC INVÁLIDA:", *errores, sep="\n - ")
    sys.exit(1)
print(f"IaC válida: {len(docs)} recursos ({', '.join(kinds)}); zona horaria y umbral versionados.")
