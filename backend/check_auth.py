"""
Script de verificación del sistema de autenticación
Ejecutar: python check_auth.py
"""

from pathlib import Path
import sys

def check_system():
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 70)
    
    checks = []
    
    # 1. Verificar base de datos
    db_path = Path(__file__).resolve().parent / "auth.db"
    print(f"\n1️⃣ Base de datos SQLite")
    if db_path.exists():
        size = db_path.stat().st_size / 1024
        print(f"   ✅ Encontrada: {db_path}")
        print(f"   📊 Tamaño: {size:.2f} KB")
        checks.append(True)
    else:
        print(f"   ❌ NO encontrada: {db_path}")
        print(f"   💡 Ejecuta: python db.py")
        checks.append(False)
    
    # 2. Verificar dependencias
    print(f"\n2️⃣ Dependencias Python")
    
    try:
        import streamlit
        print(f"   ✅ streamlit: {streamlit.__version__}")
        checks.append(True)
    except ImportError:
        print(f"   ❌ streamlit no instalado")
        checks.append(False)
    
    try:
        import streamlit_authenticator as stauth
        print(f"   ✅ streamlit-authenticator instalado")
        # Intentar detectar versión
        if hasattr(stauth, '__version__'):
            print(f"      Versión: {stauth.__version__}")
        checks.append(True)
    except ImportError:
        print(f"   ❌ streamlit-authenticator no instalado")
        checks.append(False)
    
    try:
        import bcrypt
        print(f"   ✅ bcrypt: {bcrypt.__version__}")
        checks.append(True)
    except ImportError:
        print(f"   ❌ bcrypt no instalado")
        checks.append(False)
    
    # 3. Verificar usuarios en DB
    if db_path.exists():
        print(f"\n3️⃣ Usuarios en base de datos")
        try:
            from auth_service import list_users
            users = list_users()
            print(f"   ✅ Total: {len(users)} usuarios")
            for user in users:
                print(f"      • {user['email']} ({user['role']})")
            checks.append(True)
        except Exception as e:
            print(f"   ❌ Error leyendo usuarios: {e}")
            checks.append(False)
    
    # 4. Test de autenticación
    if db_path.exists():
        print(f"\n4️⃣ Test de credenciales")
        try:
            from auth_service import authenticate
            test_result = authenticate("lankamar@gmail.com", "password123")
            if test_result:
                print(f"   ✅ Login exitoso: lankamar@gmail.com")
                print(f"      Rol: {test_result.get('role')}")
                checks.append(True)
            else:
                print(f"   ❌ Login falló (credenciales: lankamar@gmail.com / password123)")
                checks.append(False)
        except Exception as e:
            print(f"   ❌ Error en test: {e}")
            checks.append(False)
    
    # 5. Verificar archivos necesarios
    print(f"\n5️⃣ Archivos del sistema")
    required_files = [
        "db.py",
        "auth_service.py",
        "auth_adapter.py",
        "invites_service.py",
        "admin_dashboard.py"
    ]
    
    for filename in required_files:
        filepath = Path(__file__).resolve().parent / filename
        if filepath.exists():
            print(f"   ✅ {filename}")
            checks.append(True)
        else:
            print(f"   ❌ {filename} faltante")
            checks.append(False)
    
    # Resumen final
    print("\n" + "=" * 70)
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 RESULTADO: {passed}/{total} verificaciones pasadas ({percentage:.0f}%)")
    
    if passed == total:
        print("✅ Sistema completamente funcional")
        print("\n🚀 Para ejecutar el dashboard:")
        print("   streamlit run admin_dashboard.py")
        return 0
    else:
        print("❌ Se encontraron problemas")
        print("\n🔧 Pasos para reparar:")
        print("   1. pip install -r requirements.txt --upgrade")
        print("   2. python db.py")
        print("   3. python migrate_from_yaml.py")
        print("   4. python check_auth.py  # Verificar nuevamente")
        return 1

if __name__ == "__main__":
    sys.exit(check_system())
