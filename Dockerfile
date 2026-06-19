FROM ghcr.io/hexatare/posthog-railway-template/web:latest

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 python3-pil \
  && rm -rf /var/lib/apt/lists/*

COPY logo-icon.png /opt/genius/logo-icon.png
COPY patch_branding.py /opt/genius/patch_branding.py
COPY genius-entrypoint.sh /opt/genius/genius-entrypoint.sh

RUN chmod +x /opt/genius/genius-entrypoint.sh \
  && python3 /opt/genius/patch_branding.py

ENTRYPOINT ["/opt/genius/genius-entrypoint.sh"]
