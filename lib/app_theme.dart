import 'package:flutter/material.dart';

/// Tema visual clínico para el Simulador BIC Lankamar
/// Basado en colores corporativos de fabricantes médicos
class AppTheme {
  // Colores principales
  static const Color baxterBlue = Color(0xFF005EB8);
  static const Color braunGreen = Color(0xFF009640);
  static const Color clinicalWhite = Color(0xFFFAFAFA);
  static const Color alertRed = Color(0xFFD32F2F);
  static const Color warningOrange = Color(0xFFFF9800);
  static const Color successGreen = Color(0xFF4CAF50);
  
  // Colores de display/pantalla de bomba
  static const Color lcdBackground = Color(0xFF1E3A5F);
  static const Color lcdText = Color(0xFF4FC3F7);
  static const Color lcdMonochrome = Color(0xFF2E7D32);
  
  // Gradientes premium reutilizables
  static LinearGradient get primaryGradient => const LinearGradient(
    colors: [Color(0xFF0D47A1), Color(0xFF1976D2)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static LinearGradient get accentGradient => const LinearGradient(
    colors: [Color(0xFF00873C), Color(0xFF33A24A)],
    begin: Alignment.topRight,
    end: Alignment.bottomLeft,
  );
  
  /// Tema claro principal
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: baxterBlue,
        brightness: Brightness.light,
        primary: baxterBlue,
        secondary: braunGreen,
        error: alertRed,
        surface: clinicalWhite,
      ),
      
      // AppBar
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
        backgroundColor: baxterBlue,
        foregroundColor: Colors.white,
        titleTextStyle: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
      
      // Cards
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      ),
      
      // Botones elevados
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: baxterBlue,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // Botones de texto
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: baxterBlue,
          textStyle: const TextStyle(
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
      
      // SnackBar
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: const Color(0xFF323232),
        contentTextStyle: const TextStyle(
          color: Colors.white,
          fontSize: 14,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      
      // Chips
      chipTheme: ChipThemeData(
        backgroundColor: baxterBlue.withOpacity(0.1),
        labelStyle: const TextStyle(
          color: baxterBlue,
          fontWeight: FontWeight.w500,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      
      // Tipografía
      textTheme: const TextTheme(
        headlineLarge: TextStyle(
          fontSize: 28,
          fontWeight: FontWeight.bold,
          color: Color(0xFF1A1A2E),
        ),
        headlineMedium: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          color: Color(0xFF1A1A2E),
        ),
        titleLarge: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
        titleMedium: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
        bodyLarge: TextStyle(
          fontSize: 16,
          height: 1.5,
        ),
        bodyMedium: TextStyle(
          fontSize: 14,
          height: 1.4,
        ),
        labelLarge: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
  
  /// Tema oscuro (para entornos de baja luz - UCI nocturna)
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: baxterBlue,
        brightness: Brightness.dark,
        primary: const Color(0xFF64B5F6),
        secondary: const Color(0xFF81C784),
        error: const Color(0xFFEF5350),
      ),
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
        backgroundColor: Color(0xFF1A1A2E),
        foregroundColor: Colors.white,
      ),
    );
  }
}
