FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* /app/

# Force stable npm registry during image build (avoid host/global npmrc pointing to flaky mirrors)
RUN npm config set registry https://registry.npmjs.org/ \
 && npm config delete proxy || true \
 && npm config delete https-proxy || true \
 && (if [ -f package-lock.json ]; then npm ci; else npm install; fi)

COPY . /app

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
