FROM golang:alpine AS builder

WORKDIR /go/src/app
COPY ./go-src/ .
RUN apk add git
RUN CGO_ENABLED=0 go install -ldflags '-extldflags "-static"' -tags timetzdata

FROM scratch
COPY --from=builder /go/bin/golang-docker-scratch /golang-docker-scratch
COPY --from=alpine:3.22.1 /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
ENTRYPOINT ["/golang-docker-scratch"]
