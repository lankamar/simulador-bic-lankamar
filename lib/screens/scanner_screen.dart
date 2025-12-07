import 'package:flutter/material.dart';

/// Pantalla del Escáner IA (Lankamar Vision)
/// MVP: Selector manual de bomba (placeholder para ML Kit)
class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _scanController;
  bool _isScanning = false;
  String? _detectedPump;

  final List<Map<String, String>> _pumpOptions = [
    {'id': 'baxter_sigma_spectrum', 'name': 'Baxter Sigma Spectrum'},
    {'id': 'bbraun_infusomat_space', 'name': 'B. Braun Infusomat Space'},
    {'id': 'innovo_mi20', 'name': 'Innovo MI-20'},
  ];

  @override
  void initState() {
    super.initState();
    _scanController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat();
  }

  @override
  void dispose() {
    _scanController.dispose();
    super.dispose();
  }

  void _simulateScan() {
    setState(() => _isScanning = true);

    // Simular delay de escaneo
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _isScanning = false;
          // Simular detección aleatoria para demo
          _detectedPump = _pumpOptions[0]['id'];
        });

        _showDetectionResult(_pumpOptions[0]['name']!, _pumpOptions[0]['id']!);
      }
    });
  }

  void _showDetectionResult(String pumpName, String pumpId) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_circle,
                color: Colors.green,
                size: 64,
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              '¡Bomba Detectada!',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              pumpName,
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pushNamed(
                context,
                '/simulation',
                arguments: {'pumpId': pumpId},
              );
            },
            child: const Text('Ir al Simulador'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lankamar Vision'),
      ),
      body: Column(
        children: [
          // Área de cámara (placeholder)
          Expanded(
            flex: 3,
            child: Container(
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: _isScanning ? Colors.green : Colors.grey[800]!,
                  width: 3,
                ),
              ),
              child: Stack(
                children: [
                  // Fondo simulando cámara
                  ClipRRect(
                    borderRadius: BorderRadius.circular(17),
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.grey[900]!,
                            Colors.grey[850]!,
                          ],
                        ),
                      ),
                      child: Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.camera_alt,
                              size: 80,
                              color: Colors.grey[700],
                            ),
                            const SizedBox(height: 16),
                            Text(
                              _isScanning
                                  ? 'Analizando...'
                                  : 'Apuntá a la bomba de infusión',
                              style: TextStyle(
                                color: Colors.grey[500],
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  // Animación de escaneo
                  if (_isScanning)
                    AnimatedBuilder(
                      animation: _scanController,
                      builder: (context, child) {
                        return Positioned(
                          top: _scanController.value *
                              (MediaQuery.of(context).size.height * 0.35),
                          left: 0,
                          right: 0,
                          child: Container(
                            height: 3,
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: [
                                  Colors.transparent,
                                  Colors.greenAccent,
                                  Colors.transparent,
                                ],
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.greenAccent.withOpacity(0.5),
                                  blurRadius: 10,
                                  spreadRadius: 2,
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),

                  // Corners de enfoque
                  ..._buildCorners(),
                ],
              ),
            ),
          ),

          // Panel de controles
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Theme.of(context).cardColor,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(32),
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -5),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Botón de escaneo
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _isScanning ? null : _simulateScan,
                      icon: Icon(
                        _isScanning ? Icons.hourglass_top : Icons.qr_code_scanner,
                      ),
                      label: Text(
                        _isScanning ? 'Escaneando...' : 'Escanear Bomba',
                      ),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: const Color(0xFF00897B),
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),
                  const Text(
                    'O seleccioná manualmente:',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 12),

                  // Lista de selección manual
                  Expanded(
                    child: ListView.builder(
                      itemCount: _pumpOptions.length,
                      itemBuilder: (context, index) {
                        final pump = _pumpOptions[index];
                        return ListTile(
                          leading: const Icon(Icons.medical_information),
                          title: Text(pump['name']!),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () {
                            Navigator.pushNamed(
                              context,
                              '/simulation',
                              arguments: {'pumpId': pump['id']},
                            );
                          },
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  List<Widget> _buildCorners() {
    const cornerSize = 40.0;
    const cornerThickness = 4.0;
    final cornerColor = _isScanning ? Colors.greenAccent : Colors.white70;

    return [
      // Top Left
      Positioned(
        top: 16,
        left: 16,
        child: _buildCorner(cornerSize, cornerThickness, cornerColor,
            top: true, left: true),
      ),
      // Top Right
      Positioned(
        top: 16,
        right: 16,
        child: _buildCorner(cornerSize, cornerThickness, cornerColor,
            top: true, left: false),
      ),
      // Bottom Left
      Positioned(
        bottom: 16,
        left: 16,
        child: _buildCorner(cornerSize, cornerThickness, cornerColor,
            top: false, left: true),
      ),
      // Bottom Right
      Positioned(
        bottom: 16,
        right: 16,
        child: _buildCorner(cornerSize, cornerThickness, cornerColor,
            top: false, left: false),
      ),
    ];
  }

  Widget _buildCorner(
    double size,
    double thickness,
    Color color, {
    required bool top,
    required bool left,
  }) {
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        painter: _CornerPainter(
          color: color,
          thickness: thickness,
          top: top,
          left: left,
        ),
      ),
    );
  }
}

class _CornerPainter extends CustomPainter {
  final Color color;
  final double thickness;
  final bool top;
  final bool left;

  _CornerPainter({
    required this.color,
    required this.thickness,
    required this.top,
    required this.left,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = thickness
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final path = Path();

    if (top && left) {
      path.moveTo(0, size.height);
      path.lineTo(0, 0);
      path.lineTo(size.width, 0);
    } else if (top && !left) {
      path.moveTo(0, 0);
      path.lineTo(size.width, 0);
      path.lineTo(size.width, size.height);
    } else if (!top && left) {
      path.moveTo(0, 0);
      path.lineTo(0, size.height);
      path.lineTo(size.width, size.height);
    } else {
      path.moveTo(0, size.height);
      path.lineTo(size.width, size.height);
      path.lineTo(size.width, 0);
    }

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
