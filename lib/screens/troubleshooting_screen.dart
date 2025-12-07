import 'package:flutter/material.dart';
import '../services/pump_service.dart';
import '../models/pump_model.dart';

/// Pantalla de Troubleshooting - Errores y Alarmas
class TroubleshootingScreen extends StatefulWidget {
  final String? pumpId;

  const TroubleshootingScreen({super.key, this.pumpId});

  @override
  State<TroubleshootingScreen> createState() => _TroubleshootingScreenState();
}

class _TroubleshootingScreenState extends State<TroubleshootingScreen> {
  final PumpService _pumpService = PumpService();
  final TextEditingController _searchController = TextEditingController();

  Pump? _pump;
  List<PumpError> _errors = [];
  List<PumpError> _filteredErrors = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      if (widget.pumpId != null) {
        final pump = await _pumpService.getPumpById(widget.pumpId!);
        setState(() {
          _pump = pump;
          _errors = pump?.erroresYAlarmas ?? [];
          _filteredErrors = _errors;
          _isLoading = false;
        });
      } else {
        // Cargar errores de todas las bombas
        final pumps = await _pumpService.getAllPumps();
        final allErrors = <PumpError>[];
        for (final pump in pumps) {
          allErrors.addAll(pump.erroresYAlarmas);
        }
        setState(() {
          _errors = allErrors;
          _filteredErrors = allErrors;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  void _filterErrors(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredErrors = _errors;
      } else {
        _filteredErrors = _errors.where((error) {
          final lowerQuery = query.toLowerCase();
          return error.codigoPantalla.toLowerCase().contains(lowerQuery) ||
              error.significado.toLowerCase().contains(lowerQuery) ||
              error.accionCorrectiva.toLowerCase().contains(lowerQuery);
        }).toList();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_pump != null
            ? 'Errores: ${_pump!.modelo}'
            : 'Troubleshooting'),
      ),
      body: Column(
        children: [
          // Barra de búsqueda
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: TextField(
              controller: _searchController,
              onChanged: _filterErrors,
              decoration: InputDecoration(
                hintText: 'Buscar error (ej: oclusión, aire, AIR)',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _filterErrors('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Theme.of(context).scaffoldBackgroundColor,
              ),
            ),
          ),

          // Info de bomba seleccionada
          if (_pump != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: _getBrandColor(_pump!.marca).withOpacity(0.1),
              child: Row(
                children: [
                  Icon(
                    Icons.medical_information,
                    size: 20,
                    color: _getBrandColor(_pump!.marca),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _pump!.nombreCompleto,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: _getBrandColor(_pump!.marca),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    '${_filteredErrors.length} errores',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),

          // Lista de errores
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _filteredErrors.isEmpty
                    ? _buildEmptyState()
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _filteredErrors.length,
                        itemBuilder: (context, index) =>
                            _buildErrorCard(_filteredErrors[index]),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.search_off,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No se encontraron errores',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Probá con otro término de búsqueda',
            style: TextStyle(
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard(PumpError error) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.orange.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(
            Icons.warning_amber,
            color: Colors.orange,
          ),
        ),
        title: Text(
          error.codigoPantalla,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontFamily: 'monospace',
          ),
        ),
        subtitle: Text(
          error.significado,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 13,
          ),
        ),
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.green.withOpacity(0.05),
              borderRadius: const BorderRadius.vertical(
                bottom: Radius.circular(12),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.build, size: 18, color: Colors.green),
                    SizedBox(width: 8),
                    Text(
                      'Acción Correctiva',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  error.accionCorrectiva,
                  style: const TextStyle(fontSize: 14),
                ),
                const SizedBox(height: 16),

                // Botón de video (placeholder)
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _showVideoPlaceholder(error),
                    icon: const Icon(Icons.play_circle_outline),
                    label: Text('Ver video: ${error.videoTag}'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red,
                      side: const BorderSide(color: Colors.red),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showVideoPlaceholder(PumpError error) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.videocam, color: Colors.red),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                error.codigoPantalla,
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[900],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.play_circle_filled,
                      size: 64,
                      color: Colors.grey[700],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Video: ${error.videoTag}',
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontFamily: 'monospace',
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '(Conectar desde Dashboard Admin)',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              error.accionCorrectiva,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 13,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cerrar'),
          ),
        ],
      ),
    );
  }

  Color _getBrandColor(String marca) {
    switch (marca.toLowerCase()) {
      case 'baxter':
        return const Color(0xFF005EB8);
      case 'b. braun':
        return const Color(0xFF009640);
      case 'innovo':
        return const Color(0xFF455A64);
      case 'mindray':
        return const Color(0xFF00ACC1);
      case 'samtronic':
        return const Color(0xFFEF6C00);
      case 'bd':
        return const Color(0xFF7B1FA2);
      case 'fresenius kabi':
        return const Color(0xFF01579B);
      default:
        return const Color(0xFF6B7280);
    }
  }
}
