
# docker:
#  po clone
# docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -t my_dfx_rust_npm_image .
# docker run -it -v $PWD:/app my_dfx_rust_npm_image

# Wybór obrazu bazowego Ubuntu
FROM ubuntu:20.04

# Ustawienie zmiennych środowiskowych
ENV DEBIAN_FRONTEND=noninteractive

# Aktualizacja systemu i instalacja zależności
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    pkg-config \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Dodanie użytkownika 'developer' o tym samym UID i GID co użytkownik na hoście
ARG USER_ID
ARG GROUP_ID
RUN groupadd -g ${GROUP_ID} developer && \
    useradd -u ${USER_ID} -g developer -ms /bin/bash developer

# Instalacja Rust jako użytkownik 'developer'
USER developer
WORKDIR /home/developer

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/home/developer/.cargo/bin:${PATH}"

# Instalacja nvm (Node Version Manager) jako użytkownik 'developer'
USER developer
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash \
    && export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && nvm install 16.13.0 \
    && nvm use 16.13.0

# Dodajemy nvm do ścieżki
ENV NVM_DIR="/home/developer/.nvm"
ENV NODE_VERSION="16.13.0"
ENV PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"

# Instalacja DFX SDK jako użytkownik 'developer'
ENV DFXVM_INIT_YES=true
RUN curl -o- https://internetcomputer.org/install.sh | bash
ENV PATH="/home/developer/bin:${PATH}"

# Ustawienie katalogu roboczego
WORKDIR /app

# Komenda domyślna
CMD [ "bash" ]
