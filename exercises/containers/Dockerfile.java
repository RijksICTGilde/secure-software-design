# Multi-stage build for secure distroless Java container

# Stage 1: Build stage with full JDK
FROM eclipse-temurin:17-jdk-jammy AS builder

# Set working directory
WORKDIR /app

# Copy Java source code
COPY java-src/SecureApp.java .

# Compile the Java application
RUN javac SecureApp.java

# Stage 2: Runtime stage with distroless image
FROM gcr.io/distroless/java17-debian12

# Copy only the compiled bytecode from builder stage
COPY --from=builder /app/SecureApp.class /app/

# Set working directory
WORKDIR /app

# Run as non-root user (distroless automatically uses non-root)
# No shell, no package managers, minimal attack surface

# Set the entrypoint to run our Java application
ENTRYPOINT ["java", "SecureApp"]


