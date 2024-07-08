APP_NAME = metric-app
VERSION = 0.0.2

PHONY: all
all: setup-keda setup-prometheus build-app deploy-app apply-prometheus dashboard apply-scaler

PHONY: setup-keda
setup-keda:
	helm repo add kedacore https://kedacore.github.io/charts
	helm repo update
	helm install keda kedacore/keda

PHONY: setup-prometheus
setup-prometheus:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm install prometheus prometheus-community/prometheus

PHONY: build-app
build-app:
	cd metric-app && \
	docker build -t $(APP_NAME):$(VERSION) .
	kind load docker-image $(APP_NAME):$(VERSION)

PHONY: deploy-app
deploy-app:
	kubectl apply -f metric-app/deployment.yaml

PHONY: apply-prometheus
apply-prometheus:
	kubectl apply -f prometheus/prometheus.yaml 

PHONY: dashboard
dashboard:
	kubectl port-forward svc/prometheus-server 9090:80

PHONY: apply-scaler
apply-scaler:
	kubectl apply -f keda/scale-http-code.yaml

PHONY: clean
clean:
	kubectl delete -f metric-app/deployment.yaml
	kubectl delete -f keda/scale-http-code.yaml
	helm uninstall prometheus
	helm uninstall keda