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


az container show --resource-group rowling-gradproject --name rowling-backend-container --query ipAddress.ip
az container logs --resource-group rowling-gradproject --name rowling-backend-container


