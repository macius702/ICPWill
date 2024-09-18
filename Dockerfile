# docker:
#  po clone
# docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -t my_dfx_rust_npm_image .
# docker run --rm -it -v $PWD:/app -p 4943:4943 --name will_in_docker my_dfx_rust_npm_image

# https://github.com/cryptoisgood/wdfx/blob/master/docker/Dockerfile   try it ?


# Use Ubuntu 20.04 as the base image
FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libunwind8 \
    build-essential \
    libssl-dev \
    pkg-config \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    python3 python3-pip \
    wget \
    unzip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" \
    >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable

# Install Python packages (ensure Selenium is 4.6.0 or newer)
RUN pip3 install selenium>=4.6.0 colorama screeninfo

# Add 'developer' user with the same UID and GID as the host user
ARG USER_ID
ARG GROUP_ID
RUN groupadd -g ${GROUP_ID} developer && \
    useradd -u ${USER_ID} -g developer -G sudo -ms /bin/bash developer && \
    echo 'developer ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer

# Switch to 'developer' user
USER developer
WORKDIR /home/developer

# Install Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && . "$HOME/.cargo/env" \
    && rustup target add wasm32-unknown-unknown
ENV PATH="/home/developer/.cargo/bin:${PATH}"

# Install nvm (Node Version Manager)
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash \
    && export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" \
    && nvm install 20.9.0 \
    && nvm use 20.9.0

# Add nvm to PATH
ENV NVM_DIR="/home/developer/.nvm"
ENV NODE_VERSION="20.9.0"
ENV PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"

# Install latest npm
RUN npm install -g npm@10.8.3

# Install DFX SDK
ENV DFXVM_INIT_YES=true
RUN curl -o- https://internetcomputer.org/install.sh | bash
ENV PATH="/home/developer/bin:${PATH}"

# Set DFX environment variables
ENV DFX_HOST=0.0.0.0
ENV DFX_PORT=4943

# Set working directory
WORKDIR /app

# Default command
CMD [ "bash" ]
