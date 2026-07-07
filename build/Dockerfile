# Solux OS — Imagen de compilación de la ISO vía Docker
# © 2026 Pollocrudo Company
#
# Construye la ISO dentro de un contenedor Debian privilegiado (necesita loopback).
#
#   docker build -t solux-builder build/
#   docker run --privileged -v "$PWD":/solux -w /solux/build solux-builder ./build.sh
#
FROM debian:bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        live-build \
        git \
        ca-certificates \
        rsync \
        librsvg2-bin \
        xorriso \
        isolinux \
        syslinux-common \
        squashfs-tools \
        debootstrap \
        sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /solux/build

# El proyecto se monta como volumen en /solux; build.sh hace el resto.
CMD ["bash", "./build.sh"]
