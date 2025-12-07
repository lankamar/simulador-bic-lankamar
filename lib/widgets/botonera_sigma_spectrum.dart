import 'package:flutter/material.dart';

/// Widget crítico: Replica visual de la botonera Baxter Sigma Spectrum
/// Pantalla LCD Color + Soft Keys laterales + Flechas direccionales
class BotoneraSigmaSpectrum extends StatefulWidget {
  final Function(String)? onKeyPressed;
  final String displayText;
  final String statusText;
  final double? flowRate;
  final double? volumeToBeInfused;
  final bool isInfusing;

  const BotoneraSigmaSpectrum({
    super.key,
    this.onKeyPressed,
    this.displayText = 'LISTO',
    this.statusText = 'Baxter Sigma Spectrum',
    this.flowRate,
    this.volumeToBeInfused,
    this.isInfusing = false,
  });

  @override
  State<BotoneraSigmaSpectrum> createState() => _BotoneraSigmaSpectrumState();
}

class _BotoneraSigmaSpectrumState extends State<BotoneraSigmaSpectrum>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A2E), // Carcasa oscura
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.5),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header con logo
          _buildHeader(),
          const SizedBox(height: 12),

          // Área principal: Soft Keys + Pantalla
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Soft Keys Izquierda
              _buildSoftKeyColumn(isLeft: true),
              const SizedBox(width: 8),

              // Pantalla LCD Color
              _buildLCDScreen(),

              const SizedBox(width: 8),
              // Soft Keys Derecha
              _buildSoftKeyColumn(isLeft: false),
            ],
          ),

          const SizedBox(height: 16),

          // Flechas direccionales
          _buildDirectionalPad(),

          const SizedBox(height: 16),

          // Botones de acción
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Logo Baxter
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: const Color(0xFF0066B2), // Azul Baxter
            borderRadius: BorderRadius.circular(4),
          ),
          child: const Text(
            'BAXTER',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
              letterSpacing: 2,
            ),
          ),
        ),
        // Indicador de estado
        AnimatedBuilder(
          animation: _pulseController,
          builder: (context, child) {
            return Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: widget.isInfusing
                    ? Color.lerp(
                        Colors.green,
                        Colors.greenAccent,
                        _pulseController.value,
                      )
                    : Colors.orange,
                boxShadow: widget.isInfusing
                    ? [
                        BoxShadow(
                          color: Colors.green.withOpacity(0.5),
                          blurRadius: 8,
                          spreadRadius: 2,
                        ),
                      ]
                    : null,
              ),
            );
          },
        ),
        // Modelo
        const Text(
          'Sigma Spectrum',
          style: TextStyle(
            color: Colors.white70,
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildSoftKeyColumn({required bool isLeft}) {
    final labels = isLeft
        ? ['CANAL', 'OPCIONES', 'BIBLIOTECA', 'ALARMAS']
        : ['BOLUS', 'PAUSAR', 'SILENCIAR', 'AYUDA'];

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: labels.map((label) => _buildSoftKey(label)).toList(),
    );
  }

  Widget _buildSoftKey(String label) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => widget.onKeyPressed?.call(label),
          borderRadius: BorderRadius.circular(6),
          child: Container(
            width: 70,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  const Color(0xFF3D3D5C),
                  const Color(0xFF2D2D4A),
                ],
              ),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: const Color(0xFF5A5A7A),
                width: 1,
              ),
            ),
            child: Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 9,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLCDScreen() {
    return Container(
      width: 180,
      height: 220,
      decoration: BoxDecoration(
        // Gradiente de pantalla LCD color
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF1E3A5F), // Azul oscuro
            Color(0xFF0F2744), // Más oscuro
          ],
        ),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: const Color(0xFF4A6FA5),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1E88E5).withOpacity(0.2),
            blurRadius: 10,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF0D47A1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    widget.statusText,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const Icon(
                    Icons.battery_full,
                    color: Colors.greenAccent,
                    size: 14,
                  ),
                ],
              ),
            ),

            const Spacer(),

            // Display principal
            Center(
              child: Text(
                widget.displayText,
                style: const TextStyle(
                  color: Color(0xFF4FC3F7), // Cyan brillante
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
            ),

            const Spacer(),

            // Parámetros
            if (widget.flowRate != null) ...[
              _buildParameterRow('FLUJO', '${widget.flowRate} ml/h'),
            ],
            if (widget.volumeToBeInfused != null) ...[
              _buildParameterRow('VTBI', '${widget.volumeToBeInfused} ml'),
            ],

            const Spacer(),

            // Indicador de infusión
            if (widget.isInfusing)
              Center(
                child: AnimatedBuilder(
                  animation: _pulseController,
                  builder: (context, child) {
                    return Opacity(
                      opacity: 0.5 + (_pulseController.value * 0.5),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.play_arrow,
                            color: Colors.greenAccent,
                            size: 16,
                          ),
                          SizedBox(width: 4),
                          Text(
                            'INFUNDIENDO',
                            style: TextStyle(
                              color: Colors.greenAccent,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildParameterRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 11,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Color(0xFF81D4FA),
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDirectionalPad() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: const Color(0xFF2D2D4A),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Flecha arriba
          _buildArrowButton(Icons.keyboard_arrow_up, 'UP'),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildArrowButton(Icons.keyboard_arrow_left, 'LEFT'),
              const SizedBox(width: 8),
              // Botón central OK
              _buildOkButton(),
              const SizedBox(width: 8),
              _buildArrowButton(Icons.keyboard_arrow_right, 'RIGHT'),
            ],
          ),
          // Flecha abajo
          _buildArrowButton(Icons.keyboard_arrow_down, 'DOWN'),
        ],
      ),
    );
  }

  Widget _buildArrowButton(IconData icon, String action) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => widget.onKeyPressed?.call(action),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                const Color(0xFF4A4A6A),
                const Color(0xFF3A3A5A),
              ],
            ),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: const Color(0xFF6A6A8A),
              width: 1,
            ),
          ),
          child: Icon(
            icon,
            color: Colors.white,
            size: 28,
          ),
        ),
      ),
    );
  }

  Widget _buildOkButton() {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => widget.onKeyPressed?.call('OK'),
        borderRadius: BorderRadius.circular(24),
        child: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Color(0xFF0066B2),
                Color(0xFF004A82),
              ],
            ),
            shape: BoxShape.circle,
            border: Border.all(
              color: const Color(0xFF0088E0),
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF0066B2).withOpacity(0.4),
                blurRadius: 8,
                spreadRadius: 1,
              ),
            ],
          ),
          child: const Center(
            child: Text(
              'OK',
              style: TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildActionButton('INICIAR', Colors.green, Icons.play_arrow),
        _buildActionButton('DETENER', Colors.red, Icons.stop),
      ],
    );
  }

  Widget _buildActionButton(String label, Color color, IconData icon) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => widget.onKeyPressed?.call(label),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                color,
                color.withOpacity(0.7),
              ],
            ),
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.4),
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: Colors.white, size: 20),
              const SizedBox(width: 8),
              Text(
                label,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
