import 'dart:convert';
import 'package:flutter/services.dart';

class AlarmCode {
  final String code;
  final String text;
  final String priority;
  final String cause;
  final List<String> actions;
  final bool biotech;

  AlarmCode({required this.code, required this.text, required this.priority, required this.cause, required this.actions, required this.biotech});

  factory AlarmCode.fromJson(Map<String, dynamic> json) => AlarmCode(
    code: json['code'],
    text: json['text'],
    priority: json['priority'],
    cause: json['cause'],
    actions: List<String>.from(json['actions']),
    biotech: json['biotech'],
  );
}

class Device {
  final String deviceId;
  final String deviceName;
  final String manufacturer;
  final int totalCodes;
  final List<AlarmCode> alarms;

  Device({required this.deviceId, required this.deviceName, required this.manufacturer, required this.totalCodes, required this.alarms});

  factory Device.fromJson(Map<String, dynamic> json) => Device(
    deviceId: json['device_id'],
    deviceName: json['device_name'],
    manufacturer: json['manufacturer'],
    totalCodes: json['total_codes'],
    alarms: (json['alarms'] as List).map((a) => AlarmCode.fromJson(a)).toList(),
  );
}

class SimulationScenario {
  final String id;
  final String deviceId;
  final String scenarioName;
  final String context;
  final String triggerCode;
  final List<String> expectedActions;
  final int timeLimit;
  final int scoreMultiplier;

  SimulationScenario({required this.id, required this.deviceId, required this.scenarioName, required this.context, required this.triggerCode, required this.expectedActions, required this.timeLimit, required this.scoreMultiplier});

  factory SimulationScenario.fromJson(Map<String, dynamic> json) => SimulationScenario(
    id: json['id'],
    deviceId: json['device_id'],
    scenarioName: json['scenario_name'],
    context: json['context'],
    triggerCode: json['trigger_code'],
    expectedActions: List<String>.from(json['expected_actions']),
    timeLimit: json['time_limit'],
    scoreMultiplier: json['score_multiplier'],
  );
}

class AlarmService {
  static Future<Map<String, Device>> loadAllDevices() async {
    final devices = <String, Device>{};
    try {
      final plum360Json = await rootBundle.loadString('data/alarms_plum360_extended.json');
      devices['plum360'] = Device.fromJson(jsonDecode(plum360Json));
    } catch (e) { print('Error loading Plum 360: $e'); }
    return devices;
  }

  static Future<List<SimulationScenario>> loadScenarios() async {
    try {
      final scenariosJson = await rootBundle.loadString('data/simulation_scenarios.json');
      final data = jsonDecode(scenariosJson) as List;
      return data.map((s) => SimulationScenario.fromJson(s)).toList();
    } catch (e) { print('Error loading scenarios: $e'); return []; }
  }
}
