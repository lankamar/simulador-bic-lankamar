"""
Script de verificación del sistema de autenticación
Uso: python check_auth.py

Variables de entorno opcionales:
  TEST_EMAIL: Email para test de autenticación (default: lankamar@gmail.com)
  TEST_PASSWORD: Password para test (default: password123)
"""

from pathlib import Path
import sys
import os

def check_system():
    print("=" * 60)
    print("🔍 VERIFICACIÓN DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 60)
    
    checks = []
    
    # 1. Verificar que existe auth.db
    db_path = Path(__file__).resolve().parent / "auth.db"
    if db_path.exists():
        print(f"✅ Base de datos encontrada: {db_path}")
        checks.append(True)
    else:
        print(f"❌ Base de datos NO encontrada: {db_path}")
        checks.append(False)
    
    # 2. Verificar módulos
    try:
        import streamlit
        print(f"✅ Streamlit: {streamlit.__version__}")
        checks.append(True)
    except ImportError as e:
        print(f"❌ Streamlit no instalado: {e}")
        checks.append(False)
    
    try:
        import streamlit_authenticator
        print(f"✅ streamlit-authenticator instalado")
        checks.append(True)
    except ImportError as e:
        print(f"❌ streamlit-authenticator no instalado: {e}")
        checks.append(False)
    
    try:
        import bcrypt
        print(f"✅ bcrypt: {bcrypt.__version__}")
        checks.append(True)
    except ImportError as e:
        print(f"❌ bcrypt no instalado: {e}")
        checks.append(False)
    
    # 3. Verificar usuarios en DB
    if db_path.exists():
        try:
            from auth_service import list_users
            users = list_users()
            print(f"✅ Usuarios en base de datos: {len(users)}")
            for user in users:
                print(f"   - {user['email']} ({user['role']})")
            checks.append(True)
        except Exception as e:
            print(f"❌ Error leyendo usuarios: {e}")
            checks.append(False)
    
    # 4. Test de credenciales
    if db_path.exists():
        try:
            from auth_service import authenticate
            # Only test if credentials are explicitly provided via environment variables
            test_email = os.environ.get('TEST_EMAIL')
            test_password = os.environ.get('TEST_PASSWORD')
            
            if test_email and test_password:
                test_result = authenticate(test_email, test_password)
                if test_result:
                    print(f"✅ Test de login exitoso")
                    checks.append(True)
                else:
                    print(f"❌ Test de login falló con credenciales de prueba")
                    checks.append(False)
            else:
                print(f"⚠️  Test de login omitido (no hay TEST_EMAIL/TEST_PASSWORD)")
                print(f"   Ejecutar con: TEST_EMAIL=user@email.com TEST_PASSWORD=pass python check_auth.py")
                checks.append(True)  # Not a failure, just skipped
        except Exception as e:
            print(f"❌ Error en test de login: {e}")
            checks.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"RESULTADO: {passed}/{total} verificaciones pasadas")
    
    if passed == total:
        print("✅ Sistema de autenticación OK")
        return 0
    else:
        print("❌ Se encontraron problemas")
        print("\n💡 Para reparar:")
        print("   1. pip install -r requirements.txt")
        print("   2. python db.py")
        print("   3. python migrate_from_yaml.py")
        return 1

if __name__ == "__main__":
    sys.exit(check_system())
