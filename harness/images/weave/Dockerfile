# The Weave server. Builds every site from source inside the image and serves them.
# Build from the repo root:  docker build -f harness/images/weave/Dockerfile -t websim-weave .
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}
WORKDIR /srv
COPY othernet/ /srv/othernet/
# meta/ holds recorded facts (answers). Drop it so it never ships in the image.
RUN python -m othernet.build --out /srv/web --meta /tmp/meta >/dev/null && rm -rf /tmp/meta \
    && useradd --system weave && chown -R weave /srv
USER weave
ENV PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
HEALTHCHECK --interval=2s --timeout=5s --retries=30 CMD python -c "import urllib.request as u; u.urlopen(u.Request('http://127.0.0.1:8080/', headers={'Host': 'morrow.ves'}), timeout=4)"
CMD ["python", "-m", "othernet.serve", "--host", "0.0.0.0", "--port", "8080", "--web", "/srv/web"]
