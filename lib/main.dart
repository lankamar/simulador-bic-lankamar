import 'package:flutter/material.dart';
import 'app_theme.dart';
import 'screens/home_screen.dart';
import 'screens/scanner_screen.dart';
import 'screens/simulation_screen.dart';
import 'screens/troubleshooting_screen.dart';

void main() {
  runApp(const LankamarApp());
}

class LankamarApp extends StatelessWidget {
  const LankamarApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Simulador BIC Lankamar',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      initialRoute: '/',
      routes: {
        '/': (context) => const HomeScreen(),
        '/scanner': (context) => const ScannerScreen(),
        '/simulation': (context) => const SimulationScreen(),
        '/troubleshooting': (context) => const TroubleshootingScreen(),
      },
      onGenerateRoute: (settings) {
        // Rutas con parámetros
        if (settings.name == '/simulation') {
          final args = settings.arguments as Map<String, dynamic>?;
          return MaterialPageRoute(
            builder: (context) => SimulationScreen(
              pumpId: args?['pumpId'] as String?,
            ),
          );
        }
        if (settings.name == '/troubleshooting') {
          final args = settings.arguments as Map<String, dynamic>?;
          return MaterialPageRoute(
            builder: (context) => TroubleshootingScreen(
              pumpId: args?['pumpId'] as String?,
            ),
          );
        }
        return null;
      },
    );
  }
}
