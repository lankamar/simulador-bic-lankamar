/// Modelo de datos para Bombas de Infusión
/// Parseado desde pumps_db.json

class Pump {
  final String id;
  final String marca;
  final String modelo;
  final String tipo;
  final String prevalenciaArg;
  final PumpSpecs specsTecnicas;
  final PumpInterface interfaz;
  final List<PumpError> erroresYAlarmas;

  Pump({
    required this.id,
    required this.marca,
    required this.modelo,
    required this.tipo,
    required this.prevalenciaArg,
    required this.specsTecnicas,
    required this.interfaz,
    required this.erroresYAlarmas,
  });

  factory Pump.fromJson(Map<String, dynamic> json) {
    return Pump(
      id: json['id'] as String,
      marca: json['marca'] as String,
      modelo: json['modelo'] as String,
      tipo: json['tipo'] as String,
      prevalenciaArg: json['prevalencia_arg'] as String,
      specsTecnicas: PumpSpecs.fromJson(json['specs_tecnicas']),
      interfaz: PumpInterface.fromJson(json['interfaz']),
      erroresYAlarmas: (json['errores_y_alarmas'] as List)
          .map((e) => PumpError.fromJson(e))
          .toList(),
    );
  }

  /// Retorna el nombre completo para mostrar
  String get nombreCompleto => '$marca $modelo';

  /// Extrae el flujo máximo como número
  double? get flujoMaximo {
    final regex = RegExp(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)');
    final match = regex.firstMatch(specsTecnicas.rangoFlujo);
    if (match != null) {
      return double.tryParse(match.group(2) ?? '');
    }
    return null;
  }

  /// Extrae el flujo mínimo como número
  double? get flujoMinimo {
    final regex = RegExp(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)');
    final match = regex.firstMatch(specsTecnicas.rangoFlujo);
    if (match != null) {
      return double.tryParse(match.group(1) ?? '');
    }
    return null;
  }
}

class PumpSpecs {
  final String rangoFlujo;
  final String volumenMax;
  final String tipoSet;
  final String bateria;

  PumpSpecs({
    required this.rangoFlujo,
    required this.volumenMax,
    required this.tipoSet,
    required this.bateria,
  });

  factory PumpSpecs.fromJson(Map<String, dynamic> json) {
    return PumpSpecs(
      rangoFlujo: json['rango_flujo'] as String,
      volumenMax: json['volumen_max'] as String,
      tipoSet: json['tipo_set'] as String,
      bateria: json['bateria'] as String,
    );
  }

  /// Extrae volumen máximo como número
  int? get volumenMaxNumerico {
    final regex = RegExp(r'(\d+)');
    final match = regex.firstMatch(volumenMax);
    if (match != null) {
      return int.tryParse(match.group(1) ?? '');
    }
    return null;
  }
}

class PumpInterface {
  final String pantalla;
  final String teclado;
  final String navegacion;

  PumpInterface({
    required this.pantalla,
    required this.teclado,
    required this.navegacion,
  });

  factory PumpInterface.fromJson(Map<String, dynamic> json) {
    return PumpInterface(
      pantalla: json['pantalla'] as String,
      teclado: json['teclado'] as String,
      navegacion: json['navegacion'] as String,
    );
  }

  /// Determina si es pantalla color o monocroma
  bool get esPantallaColor =>
      pantalla.toLowerCase().contains('color') ||
      pantalla.toLowerCase().contains('tft');
}

class PumpError {
  final String codigoPantalla;
  final String significado;
  final String accionCorrectiva;
  final String videoTag;

  PumpError({
    required this.codigoPantalla,
    required this.significado,
    required this.accionCorrectiva,
    required this.videoTag,
  });

  factory PumpError.fromJson(Map<String, dynamic> json) {
    return PumpError(
      codigoPantalla: json['codigo_pantalla'] as String,
      significado: json['significado'] as String,
      accionCorrectiva: json['accion_correctiva'] as String,
      videoTag: json['video_tag'] as String,
    );
  }

  /// Normaliza el código para búsqueda
  String get codigoNormalizado {
    return codigoPantalla
        .toUpperCase()
        .replaceAll(RegExp(r'[:\-_]'), ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }
}
