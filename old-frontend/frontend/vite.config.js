import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, 
    allowedHosts: [
      'spindliest-mari-squashily.ngrok-free.dev'
    ]
  }
})