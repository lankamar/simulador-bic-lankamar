import 'package:flutter/material.dart';

/// Widget: Replica visual de la botonera B. Braun Infusomat Space
/// Diseño modular vertical con pantalla TFT Color y navegación por flechas
class BotoneraInfusomatSpace extends StatefulWidget {
  final Function(String)? onKeyPressed;
  final String displayText;
  final String statusText;
  final double? flowRate;
  final double? volumeToBeInfused;
  final bool isInfusing;

  const BotoneraInfusomatSpace({
    super.key,
    this.onKeyPressed,
    this.displayText = 'LISTO',
    this.statusText = 'B. Braun Infusomat Space',
    this.flowRate,
    this.volumeToBeInfused,
    this.isInfusing = false,
  });

  @override
  State<BotoneraInfusomatSpace> createState() => _BotoneraInfusomatSpaceState();
}

class _BotoneraInfusomatSpaceState extends State<BotoneraInfusomatSpace>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
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
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        // Carcasa blanca característica de B.Braun
        color: const Color(0xFFF5F5F5),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: const Color(0xFF009640), // Verde Braun
          width: 3,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header con logo B.Braun
          _buildHeader(),
          const SizedBox(height: 8),

          // Pantalla TFT Color
          _buildTFTScreen(),

          const SizedBox(height: 12),

          // Teclado numérico virtual
          _buildVirtualKeypad(),

          const SizedBox(height: 12),

          // Flechas de navegación
          _buildNavigationArrows(),

          const SizedBox(height: 12),

          // Botones de acción inferiores
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Logo B.Braun
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: const Color(0xFF009640), // Verde Braun
            borderRadius: BorderRadius.circular(4),
          ),
          child: const Text(
            'B|BRAUN',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 11,
              letterSpacing: 1,
            ),
          ),
        ),
        // Indicador LED de estado
        AnimatedBuilder(
          animation: _pulseController,
          builder: (context, child) {
            return Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: widget.isInfusing
                    ? Color.lerp(
                        const Color(0xFF009640),
                        const Color(0xFF4CAF50),
                        _pulseController.value,
                      )
                    : Colors.orange,
                boxShadow: widget.isInfusing
                    ? [
                        BoxShadow(
                          color: const Color(0xFF009640).withOpacity(0.6),
                          blurRadius: 6,
                          spreadRadius: 2,
                        ),
                      ]
                    : null,
              ),
            );
          },
        ),
        // Nombre del modelo
        const Text(
          'Infusomat Space',
          style: TextStyle(
            color: Color(0xFF333333),
            fontSize: 10,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildTFTScreen() {
    return Container(
      width: 200,
      height: 180,
      decoration: BoxDecoration(
        // Pantalla TFT con gradiente azul/negro
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFF1565C0), // Azul más claro arriba
            Color(0xFF0D47A1), // Azul oscuro abajo
          ],
        ),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: const Color(0xFF424242),
          width: 3,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Barra de estado superior
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
              decoration: BoxDecoration(
                color: const Color(0xFF0D47A1),
                borderRadius: BorderRadius.circular(3),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    widget.statusText,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 9,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.battery_full, 
                          color: Colors.greenAccent, size: 12),
                      const SizedBox(width: 4),
                      Text(
                        widget.isInfusing ? '▶' : '⏸',
                        style: TextStyle(
                          color: widget.isInfusing 
                              ? Colors.greenAccent 
                              : Colors.orange,
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const Spacer(),

            // Display principal centrado
            Center(
              child: Text(
                widget.displayText,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ),

            const Spacer(),

            // Parámetros de infusión
            if (widget.flowRate != null)
              _buildParameterRow('FLUJO', '${widget.flowRate} ml/h'),
            if (widget.volumeToBeInfused != null)
              _buildParameterRow('VTBI', '${widget.volumeToBeInfused} ml'),

            const Spacer(),

            // Indicador de infusión
            if (widget.isInfusing)
              Center(
                child: AnimatedBuilder(
                  animation: _pulseController,
                  builder: (context, child) {
                    return Opacity(
                      opacity: 0.6 + (_pulseController.value * 0.4),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF009640).withOpacity(0.3),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          '● INFUNDIENDO',
                          style: TextStyle(
                            color: Colors.greenAccent,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
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
      padding: const EdgeInsets.symmetric(vertical: 1),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              color: Colors.white60,
              fontSize: 10,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Color(0xFF81D4FA),
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildVirtualKeypad() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: const Color(0xFFE0E0E0),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          // Fila 1: 1-2-3
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildNumKey('1'),
              _buildNumKey('2'),
              _buildNumKey('3'),
            ],
          ),
          const SizedBox(height: 4),
          // Fila 2: 4-5-6
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildNumKey('4'),
              _buildNumKey('5'),
              _buildNumKey('6'),
            ],
          ),
          const SizedBox(height: 4),
          // Fila 3: 7-8-9
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildNumKey('7'),
              _buildNumKey('8'),
              _buildNumKey('9'),
            ],
          ),
          const SizedBox(height: 4),
          // Fila 4: C-0-OK
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildNumKey('C', color: Colors.orange),
              _buildNumKey('0'),
              _buildNumKey('OK', color: const Color(0xFF009640)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNumKey(String label, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.all(2),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => widget.onKeyPressed?.call(label),
          borderRadius: BorderRadius.circular(6),
          child: Container(
            width: 44,
            height: 36,
            decoration: BoxDecoration(
              color: color ?? Colors.white,
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: const Color(0xFFBDBDBD)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 2,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Center(
              child: Text(
                label,
                style: TextStyle(
                  color: color != null ? Colors.white : Colors.black87,
                  fontWeight: FontWeight.bold,
                  fontSize: label.length > 1 ? 11 : 14,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavigationArrows() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _buildArrowButton(Icons.keyboard_arrow_left, 'LEFT'),
        Column(
          children: [
            _buildArrowButton(Icons.keyboard_arrow_up, 'UP'),
            const SizedBox(height: 4),
            _buildArrowButton(Icons.keyboard_arrow_down, 'DOWN'),
          ],
        ),
        _buildArrowButton(Icons.keyboard_arrow_right, 'RIGHT'),
      ],
    );
  }

  Widget _buildArrowButton(IconData icon, String action) {
    return Padding(
      padding: const EdgeInsets.all(2),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => widget.onKeyPressed?.call(action),
          borderRadius: BorderRadius.circular(6),
          child: Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFF009640),
              borderRadius: BorderRadius.circular(6),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF009640).withOpacity(0.3),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Icon(icon, color: Colors.white, size: 24),
          ),
        ),
      ),
    );
  }

  Widget _buildActionButtons() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildActionButton('INICIAR', const Color(0xFF009640), Icons.play_arrow),
        _buildActionButton('PAUSAR', Colors.orange, Icons.pause),
        _buildActionButton('DETENER', Colors.red, Icons.stop),
      ],
    );
  }

  Widget _buildActionButton(String label, Color color, IconData icon) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => widget.onKeyPressed?.call(label),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(8),
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.4),
                blurRadius: 6,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: Colors.white, size: 18),
              const SizedBox(width: 4),
              Text(
                label,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
