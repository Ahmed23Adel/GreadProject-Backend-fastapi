az container create \
  --resource-group rowling-gradproject \
  --name rowling-backend-container \
  --image ahmedadelabdelmohsen/rowling-gradproject:latest \
  --dns-name-label rowling-backend \
  --ports 8000 \
  --environment-variables PORT=8000 \
  --registry-login-server index.docker.io \
  --registry-username ahmedadelabdelmohsen \
  --registry-password waxdoj-naqRa2-vybhaf
  --log-analytics-workspace 6db8b2de-324c-4297-b7c5-200ea517b3d4 \
  --log-analytics-workspace-key oilmm/4Hvdia8hSpWCiWotch81F/Ak8N+s8yyl1ZySkezTu077l4Ac96XxDzXu1y7MVNE0B0g5kaMUz9hyqO2Q==



az container show --resource-group rowling-gradproject --name rowling-backend-container --query ipAddress.ip
az container logs --resource-group rowling-gradproject --name rowling-backend-container


Workspace ID
6db8b2de-324c-4297-b7c5-200ea517b3d4

Primary key
oilmm/4Hvdia8hSpWCiWotch81F/Ak8N+s8yyl1ZySkezTu077l4Ac96XxDzXu1y7MVNE0B0g5kaMUz9hyqO2Q==

az container update \
    --resource-group rowling-gradproject \
    --name rowling-backend-container \
    --log-analytics-workspace 6db8b2de-324c-4297-b7c5-200ea517b3d4 \
    --log-analytics-workspace-key oilmm/4Hvdia8hSpWCiWotch81F/Ak8N+s8yyl1ZySkezTu077l4Ac96XxDzXu1y7MVNE0B0g5kaMUz9hyqO2Q==


az container create \
    --resource-group rowling-gradproject \
    --name rowling-backend-container2 \
    --image ahmedadelabdelmohsen/rowling-gradproject:latest \
    --dns-name-label rowling-backend2 \
    --ports 8000 \
    --environment-variables PORT=8000 \
    --registry-login-server index.docker.io \
    --registry-username ahmedadelabdelmohsen \
    --registry-password waxdoj-naqRa2-vybhaf \
    --log-analytics-workspace 6db8b2de-324c-4297-b7c5-200ea517b3d4 \
    --log-analytics-workspace-key oilmm/4Hvdia8hSpWCiWotch81F/Ak8N+s8yyl1ZySkezTu077l4Ac96XxDzXu1y7MVNE0B0g5kaMUz9hyqO2Q==
uvicorn main:app --host 0.0.0.0 --port 8000