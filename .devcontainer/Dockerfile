# Optional extension of the scipy-notebook base image.
# Add system packages here as needed.
# Example:
#   RUN apt-get update && apt-get install -y --no-install-recommends \
#         git-lfs \
#       && rm -rf /var/lib/apt/lists/*
FROM quay.io/jupyter/scipy-notebook:latest

# Switch to root only for system-level changes, then restore the
# unprivileged notebook user so JupyterLab file permissions stay correct.
USER root

USER ${NB_UID}
