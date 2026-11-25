ARG UBUNTU_VERSION=24.04
FROM ubuntu:${UBUNTU_VERSION} AS sim

ARG ROS_DISTRO=jazzy
ARG ROS_PACKAGE=desktop
ARG DEBIAN_FRONTEND=noninteractive

ENV ROS_DISTRO=${ROS_DISTRO} \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl git locales \
    && locale-gen en_US.UTF-8 \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
        > /etc/apt/sources.list.d/ros2.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        ros-${ROS_DISTRO}-${ROS_PACKAGE} ros-${ROS_DISTRO}-control-msgs \
        python3-pip python3-colcon-common-extensions \
        build-essential cmake zsh tmux libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages mujoco catmux

# zsh as login shell so catmux/tmux panes use it
RUN usermod -s /usr/bin/zsh ubuntu
USER ubuntu
WORKDIR /home/ubuntu
