#!/usr/bin/env python3
"""
Script para probar la conexión WebSocket manualmente
"""
import socketio
import time

# Crear cliente Socket.IO
sio = socketio.SimpleClient()

try:
    print("🔗 Intentando conectar a WebSocket...")
    sio.connect('http://localhost:5001')
    print("✅ Conectado exitosamente!")
    
    # Enviar evento de suscripción
    print("📡 Enviando suscripción para libro ID 32...")
    sio.emit('subscribe_book_progress', {
        'book_uuid': 'a04c656c-af7e-4ba8-8f19-816104a44478'
    })
    
    # Esperar respuesta
    print("⏳ Esperando respuesta...")
    time.sleep(5)
    
    # Desconectar
    sio.disconnect()
    print("🔌 Desconectado")
    
except Exception as e:
    print(f"❌ Error: {e}")