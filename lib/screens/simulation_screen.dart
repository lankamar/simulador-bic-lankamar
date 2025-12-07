import 'package:flutter/material.dart';
import '../services/pump_service.dart';
import '../models/pump_model.dart';
import '../widgets/botonera_sigma_spectrum.dart';
import '../widgets/botonera_infusomat_space.dart';
import '../widgets/botonera_mi20.dart';

/// Pantalla del Simulador Interactivo
class SimulationScreen extends StatefulWidget {
  final String? pumpId;

  const SimulationScreen({super.key, this.pumpId});

  @override
  State<SimulationScreen> createState() => _SimulationScreenState();
}

class _SimulationScreenState extends State<SimulationScreen> {
  final PumpService _pumpService = PumpService();
  Pump? _pump;
  bool _isLoading = true;

  // Estado del simulador
  String _displayText = 'LISTO';
  String _statusText = 'Cargando...';
  double? _flowRate;
  double? _vtbi;
  bool _isInfusing = false;
  String _currentMenu = 'main';

  @override
  void initState() {
    super.initState();
    _loadPump();
  }

  Future<void> _loadPump() async {
    final pumpId = widget.pumpId ?? 'baxter_sigma_spectrum';
    try {
      final pump = await _pumpService.getPumpById(pumpId);
      setState(() {
        _pump = pump;
        _statusText = pump?.nombreCompleto ?? 'Bomba no encontrada';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _statusText = 'Error al cargar';
      });
    }
  }

  void _handleKeyPress(String key) {
    setState(() {
      switch (key) {
        case 'INICIAR':
          if (_flowRate != null && _vtbi != null) {
            _isInfusing = true;
            _displayText = 'INFUNDIENDO';
          } else {
            _displayText = 'PROGRAMAR PRIMERO';
          }
          break;

        case 'DETENER':
          _isInfusing = false;
          _displayText = 'DETENIDO';
          break;

        case 'PAUSAR':
          if (_isInfusing) {
            _isInfusing = false;
            _displayText = 'PAUSADO';
          }
          break;

        case 'CANAL':
          _displayText = 'CANAL A';
          _currentMenu = 'channel';
          break;

        case 'OPCIONES':
          _displayText = 'OPCIONES';
          _currentMenu = 'options';
          break;

        case 'BIBLIOTECA':
          _displayText = 'DRUG LIBRARY';
          _currentMenu = 'library';
          break;

        case 'ALARMAS':
          _displayText = 'SIN ALARMAS';
          break;

        case 'BOLUS':
          _displayText = 'BOLUS MANUAL';
          break;

        case 'SILENCIAR':
          _displayText = 'SILENCIADO 2min';
          break;

        case 'AYUDA':
          _showHelp();
          break;

        case 'UP':
          if (_currentMenu == 'flow') {
            _flowRate = (_flowRate ?? 0) + 10;
            if (_flowRate! > (_pump?.flujoMaximo ?? 999)) {
              _flowRate = _pump?.flujoMaximo ?? 999;
            }
            _displayText = 'FLUJO: ${_flowRate?.toInt()} ml/h';
          } else if (_currentMenu == 'vtbi') {
            _vtbi = (_vtbi ?? 0) + 50;
            _displayText = 'VTBI: ${_vtbi?.toInt()} ml';
          }
          break;

        case 'DOWN':
          if (_currentMenu == 'flow') {
            _flowRate = (_flowRate ?? 100) - 10;
            if (_flowRate! < (_pump?.flujoMinimo ?? 0.5)) {
              _flowRate = _pump?.flujoMinimo ?? 0.5;
            }
            _displayText = 'FLUJO: ${_flowRate?.toInt()} ml/h';
          } else if (_currentMenu == 'vtbi') {
            _vtbi = (_vtbi ?? 100) - 50;
            if (_vtbi! < 0) _vtbi = 0;
            _displayText = 'VTBI: ${_vtbi?.toInt()} ml';
          }
          break;

        case 'LEFT':
          _currentMenu = 'flow';
          _displayText = 'AJUSTAR FLUJO';
          break;

        case 'RIGHT':
          _currentMenu = 'vtbi';
          _displayText = 'AJUSTAR VTBI';
          break;

        case 'OK':
          if (_currentMenu == 'flow' || _currentMenu == 'vtbi') {
            _currentMenu = 'main';
            _displayText = 'PROGRAMADO';
          }
          break;
      }
    });
  }

  void _showHelp() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Ayuda del Simulador'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHelpItem('← Izquierda', 'Ajustar flujo'),
            _buildHelpItem('→ Derecha', 'Ajustar VTBI'),
            _buildHelpItem('↑↓ Flechas', 'Subir/Bajar valores'),
            _buildHelpItem('OK', 'Confirmar'),
            _buildHelpItem('INICIAR', 'Comenzar infusión'),
            _buildHelpItem('DETENER', 'Detener infusión'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Entendido'),
          ),
        ],
      ),
    );
  }

  Widget _buildHelpItem(String key, String description) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              key,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Text(description),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_pump?.nombreCompleto ?? 'Simulador'),
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: _showHelp,
          ),
          IconButton(
            icon: const Icon(Icons.warning_amber),
            onPressed: () {
              Navigator.pushNamed(
                context,
                '/troubleshooting',
                arguments: {'pumpId': widget.pumpId},
              );
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Theme.of(context).scaffoldBackgroundColor,
                    Theme.of(context).scaffoldBackgroundColor.withOpacity(0.8),
                  ],
                ),
              ),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Info de la bomba
                    if (_pump != null) _buildPumpInfo(),

                    const SizedBox(height: 24),

                    // Widget de la botonera según el modelo
                    _buildPumpSimulator(),

                    const SizedBox(height: 24),

                    // Panel de estado
                    _buildStatusPanel(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildPumpInfo() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            const Icon(Icons.info_outline, color: Colors.blue),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Rango de flujo: ${_pump!.specsTecnicas.rangoFlujo}',
                    style: const TextStyle(fontSize: 13),
                  ),
                  Text(
                    'Set: ${_pump!.specsTecnicas.tipoSet}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPumpSimulator() {
    if (_pump == null) {
      return const Center(child: Text('Bomba no encontrada'));
    }

    final marca = _pump!.marca.toLowerCase();
    final teclado = _pump!.interfaz.teclado.toLowerCase();

    // Lógica dinámica según marca/interfaz (como especifica el Prompt Maestro)
    if (marca == 'baxter' || teclado.contains('soft keys')) {
      return BotoneraSigmaSpectrum(
        onKeyPressed: _handleKeyPress,
        displayText: _displayText,
        statusText: _statusText,
        flowRate: _flowRate,
        volumeToBeInfused: _vtbi,
        isInfusing: _isInfusing,
      );
    } else if (marca == 'b. braun' || marca == 'b.braun' || marca == 'braun') {
      return BotoneraInfusomatSpace(
        onKeyPressed: _handleKeyPress,
        displayText: _displayText,
        statusText: _statusText,
        flowRate: _flowRate,
        volumeToBeInfused: _vtbi,
        isInfusing: _isInfusing,
      );
    } else if (marca == 'innovo' || teclado.contains('botones físicos') || teclado.contains('físicos')) {
      return BotoneraMI20(
        onKeyPressed: _handleKeyPress,
        displayText: _displayText,
        statusText: _statusText,
        flowRate: _flowRate,
        volumeToBeInfused: _vtbi,
        isInfusing: _isInfusing,
      );
    } else if (teclado.contains('híbrido') || marca == 'mindray') {
      // Mindray y otros híbridos - por ahora usar Braun como aproximación
      return BotoneraInfusomatSpace(
        onKeyPressed: _handleKeyPress,
        displayText: _displayText,
        statusText: '${_pump!.marca} ${_pump!.modelo} (Simulación Aproximada)',
        flowRate: _flowRate,
        volumeToBeInfused: _vtbi,
        isInfusing: _isInfusing,
      );
    } else {
      // Fallback genérico (Samtronic, BD, Fresenius, etc.)
      // Usar MI-20 como base para equipos con botones físicos
      return BotoneraMI20(
        onKeyPressed: _handleKeyPress,
        displayText: _displayText,
        statusText: '${_pump!.marca} ${_pump!.modelo} (Genérico)',
        flowRate: _flowRate,
        volumeToBeInfused: _vtbi,
        isInfusing: _isInfusing,
      );
    }
  }

  Widget _buildStatusPanel() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Estado Actual',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const Divider(),
            _buildStatusRow('Menú activo', _currentMenu.toUpperCase()),
            _buildStatusRow(
              'Flujo programado',
              _flowRate != null ? '${_flowRate!.toInt()} ml/h' : 'No configurado',
            ),
            _buildStatusRow(
              'VTBI',
              _vtbi != null ? '${_vtbi!.toInt()} ml' : 'No configurado',
            ),
            _buildStatusRow(
              'Estado',
              _isInfusing ? '🟢 Infundiendo' : '🟡 Detenido',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(color: Colors.grey[600]),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}
