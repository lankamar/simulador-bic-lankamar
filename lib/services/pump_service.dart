import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import '../models/pump_model.dart';

/// Servicio para cargar y gestionar datos de bombas de infusión
/// Implementa patrón Singleton para acceso global
class PumpService {
  static final PumpService _instance = PumpService._internal();
  factory PumpService() => _instance;
  PumpService._internal();

  List<Pump>? _pumps;
  bool _isLoaded = false;

  /// Carga los datos desde el JSON local
  Future<void> loadPumps() async {
    if (_isLoaded) return;

    try {
      final String jsonString =
          await rootBundle.loadString('assets/data/pumps_db.json');
      final List<dynamic> jsonList = json.decode(jsonString);
      _pumps = jsonList.map((json) => Pump.fromJson(json)).toList();
      _isLoaded = true;
    } catch (e) {
      throw Exception('Error al cargar datos de bombas: $e');
    }
  }

  /// Retorna todas las bombas disponibles
  Future<List<Pump>> getAllPumps() async {
    await loadPumps();
    return _pumps ?? [];
  }

  /// Busca una bomba por ID
  Future<Pump?> getPumpById(String id) async {
    await loadPumps();
    try {
      return _pumps?.firstWhere((pump) => pump.id == id);
    } catch (e) {
      return null;
    }
  }

  /// Retorna todos los errores de una bomba específica
  Future<List<PumpError>> getErrorsByPumpId(String pumpId) async {
    final pump = await getPumpById(pumpId);
    return pump?.erroresYAlarmas ?? [];
  }

  /// Busca errores en todas las bombas por texto
  Future<List<SearchResult>> searchErrors(String query) async {
    await loadPumps();
    final results = <SearchResult>[];
    final normalizedQuery = query.toLowerCase().trim();

    for (final pump in _pumps ?? []) {
      for (final error in pump.erroresYAlarmas) {
        if (error.codigoPantalla.toLowerCase().contains(normalizedQuery) ||
            error.significado.toLowerCase().contains(normalizedQuery) ||
            error.accionCorrectiva.toLowerCase().contains(normalizedQuery)) {
          results.add(SearchResult(pump: pump, error: error));
        }
      }
    }

    return results;
  }

  /// Valida si un flujo está dentro del rango permitido
  Future<bool> isFlowRateValid(String pumpId, double flowRate) async {
    final pump = await getPumpById(pumpId);
    if (pump == null) return false;

    final min = pump.flujoMinimo ?? 0;
    final max = pump.flujoMaximo ?? double.infinity;

    return flowRate >= min && flowRate <= max;
  }

  /// Retorna bombas filtradas por marca
  Future<List<Pump>> getPumpsByBrand(String marca) async {
    await loadPumps();
    return _pumps
            ?.where(
                (pump) => pump.marca.toLowerCase() == marca.toLowerCase())
            .toList() ??
        [];
  }
}

/// Resultado de búsqueda que incluye la bomba y el error encontrado
class SearchResult {
  final Pump pump;
  final PumpError error;

  SearchResult({required this.pump, required this.error});
}
