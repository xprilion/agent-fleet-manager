from flask import Flask, request, jsonify, render_template
from kubernetes import client, config

app = Flask(__name__)

# Load kube config for local development
config.load_kube_config()

k8s_client = client.AppsV1Api()
core_v1_client = client.CoreV1Api()

# Deployment name and namespace
DEPLOYMENT_NAME = 'agent-fleet'
NAMESPACE = 'default'


@app.route('/')
def index():
    # Fetch the current status of agents
    agents = get_agents()
    return render_template('index.html', agents=agents)


@app.route('/add_agent', methods=['POST'])
def add_agent():
    data = request.json
    title = data.get("title")
    personality = data.get('description')
    replicas = data.get('replicas')
    
    pod_name = f"agent-{title.replace(' ', '-').lower()}"

    pod_body = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "labels": {
                "app": "agent-fleet"
            }
        },
        "replicas": replicas,
        "spec": {
            "containers": [
                {
                    "name": "agent-fleet",
                    "image": "docker.io/library/agent-fleet:13",
                    "ports": [
                        {"containerPort": 5000}
                    ],
                    "env": [
                        {"name": "TITLE", "value": title},
                        {"name": "PERSONALITY", "value": personality}
                    ],
                    "imagePullPolicy": "Never"
                }
            ]
        }
    }
    try:
        # Create the pod with unique environment variables
        core_v1_client.create_namespaced_pod(namespace=NAMESPACE, body=pod_body)
        return jsonify({'status': 'success', 'pod_name': pod_name}), 200
    
    except client.exceptions.ApiException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/remove_agent/<agent_id>', methods=['DELETE'])
def remove_agent(agent_id):
    pod_name = f"{agent_id.replace(' ', '-').lower()}"  # Construct the pod name based on agent_id
    
    try:
        # Delete the specific pod
        core_v1_client.delete_namespaced_pod(name=pod_name, namespace=NAMESPACE)
        
        return jsonify({'status': 'success', 'pod_name': pod_name}), 200
    
    except client.exceptions.ApiException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/agents', methods=['GET'])
def get_agents():
    try:
        pods = core_v1_client.list_namespaced_pod(namespace=NAMESPACE, label_selector='app=agent-fleet')
        agents = [{'id': pod.metadata.name, 'status': pod.status.phase} for pod in pods.items]
        return agents
    except client.exceptions.ApiException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
