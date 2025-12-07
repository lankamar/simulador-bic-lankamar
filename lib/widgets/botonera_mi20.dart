import 'package:flutter/material.dart';

/// Widget: Replica visual de la botonera Innovo MI-20
/// Pantalla LCD Monocroma simple con botones físicos rígidos
/// Diseño económico típico de hospitales públicos/provinciales
class BotoneraMI20 extends StatefulWidget {
  final Function(String)? onKeyPressed;
  final String displayText;
  final String statusText;
  final double? flowRate;
  final double? volumeToBeInfused;
  final bool isInfusing;

  const BotoneraMI20({
    super.key,
    this.onKeyPressed,
    this.displayText = 'LISTO',
    this.statusText = 'Innovo MI-20',
    this.flowRate,
    this.volumeToBeInfused,
    this.isInfusing = false,
  });

  @override
  State<BotoneraMI20> createState() => _BotoneraMI20State();
}

class _BotoneraMI20State extends State<BotoneraMI20>
    with SingleTickerProviderStateMixin {
  late AnimationController _blinkController;

  @override
  void initState() {
    super.initState();
    _blinkController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _blinkController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        // Carcasa plástica gris típica de equipos económicos
        color: const Color(0xFFB0BEC5), // Gris azulado
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFF78909C),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.25),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header con marca
          _buildHeader(),
          const SizedBox(height: 10),

          // Pantalla LCD Monocroma
          _buildLCDMonoScreen(),

          const SizedBox(height: 14),

          // Fila de botones físicos rígidos
          _buildPhysicalButtonRow(),

          const SizedBox(height: 10),

          // Botones numéricos simples
          _buildSimpleNumpad(),

          const SizedBox(height: 14),

          // Botones de control principales
          _buildMainControlButtons(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Logo Innovo (marca genérica)
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
          decoration: BoxDecoration(
            color: const Color(0xFF37474F),
            borderRadius: BorderRadius.circular(4),
          ),
          child: const Text(
            'INNOVO',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 10,
              letterSpacing: 1.5,
            ),
          ),
        ),
        // LED indicador simple
        Row(
          children: [
            // LED de encendido
            Container(
              width: 8,
              height: 8,
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.green,
              ),
            ),
            const SizedBox(width: 6),
            // LED de alarma (parpadea si hay problema)
            AnimatedBuilder(
              animation: _blinkController,
              builder: (context, child) {
                return Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: widget.isInfusing
                        ? Colors.transparent
                        : Color.lerp(
                            Colors.red,
                            Colors.transparent,
                            _blinkController.value,
                          ),
                  ),
                );
              },
            ),
          ],
        ),
        // Modelo
        const Text(
          'MI-20',
          style: TextStyle(
            color: Color(0xFF37474F),
            fontSize: 11,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildLCDMonoScreen() {
    return Container(
      width: 180,
      height: 100,
      decoration: BoxDecoration(
        // Pantalla LCD verde monocroma clásica
        color: const Color(0xFF9CCC65), // Verde LCD
        borderRadius: BorderRadius.circular(4),
        border: Border.all(
          color: const Color(0xFF558B2F),
          width: 3,
        ),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF558B2F).withOpacity(0.3),
            blurRadius: 8,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Línea de estado (pequeña)
            Text(
              widget.statusText,
              style: const TextStyle(
                color: Color(0xFF33691E),
                fontSize: 9,
                fontWeight: FontWeight.w500,
                fontFamily: 'monospace',
              ),
            ),

            const Spacer(),

            // Display principal - Texto grande monocromo
            Center(
              child: Text(
                widget.displayText,
                style: const TextStyle(
                  color: Color(0xFF1B5E20), // Verde muy oscuro
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  fontFamily: 'monospace',
                  letterSpacing: 2,
                ),
              ),
            ),

            const Spacer(),

            // Parámetros en formato simple
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (widget.flowRate != null)
                  Text(
                    'F:${widget.flowRate?.toInt()}ml/h',
                    style: const TextStyle(
                      color: Color(0xFF33691E),
                      fontSize: 10,
                      fontFamily: 'monospace',
                    ),
                  ),
                if (widget.volumeToBeInfused != null)
                  Text(
                    'V:${widget.volumeToBeInfused?.toInt()}ml',
                    style: const TextStyle(
                      color: Color(0xFF33691E),
                      fontSize: 10,
                      fontFamily: 'monospace',
                    ),
                  ),
                if (widget.isInfusing)
                  AnimatedBuilder(
                    animation: _blinkController,
                    builder: (context, child) {
                      return Opacity(
                        opacity: 0.5 + (_blinkController.value * 0.5),
                        child: const Text(
                          '►RUN',
                          style: TextStyle(
                            color: Color(0xFF1B5E20),
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            fontFamily: 'monospace',
                          ),
                        ),
                      );
                    },
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPhysicalButtonRow() {
    // Fila de botones de función (típico de equipos económicos)
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildPhysicalButton('MENU', Icons.menu),
        _buildPhysicalButton('◀', Icons.arrow_left),
        _buildPhysicalButton('▲', Icons.arrow_drop_up),
        _buildPhysicalButton('▼', Icons.arrow_drop_down),
        _buildPhysicalButton('▶', Icons.arrow_right),
        _buildPhysicalButton('ENTER', Icons.check),
      ],
    );
  }

  Widget _buildPhysicalButton(String label, IconData icon) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          // Mapear iconos a acciones
          String action = label;
          if (label == '▲') action = 'UP';
          if (label == '▼') action = 'DOWN';
          if (label == '◀') action = 'LEFT';
          if (label == '▶') action = 'RIGHT';
          if (label == 'ENTER') action = 'OK';
          widget.onKeyPressed?.call(action);
        },
        borderRadius: BorderRadius.circular(4),
        child: Container(
          width: 38,
          height: 32,
          decoration: BoxDecoration(
            // Botones de plástico rígido gris oscuro
            color: const Color(0xFF455A64),
            borderRadius: BorderRadius.circular(4),
            border: Border.all(
              color: const Color(0xFF37474F),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 2,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Center(
            child: label.length <= 2
                ? Text(
                    label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  )
                : Text(
                    label,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 7,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
          ),
        ),
      ),
    );
  }

  Widget _buildSimpleNumpad() {
    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: const Color(0xFF90A4AE),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildNumButton('1'),
              _buildNumButton('2'),
              _buildNumButton('3'),
              _buildNumButton('4'),
              _buildNumButton('5'),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildNumButton('6'),
              _buildNumButton('7'),
              _buildNumButton('8'),
              _buildNumButton('9'),
              _buildNumButton('0'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNumButton(String num) {
    return Padding(
      padding: const EdgeInsets.all(2),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => widget.onKeyPressed?.call(num),
          borderRadius: BorderRadius.circular(4),
          child: Container(
            width: 32,
            height: 28,
            decoration: BoxDecoration(
              color: const Color(0xFF546E7A),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: const Color(0xFF455A64)),
            ),
            child: Center(
              child: Text(
                num,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMainControlButtons() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildMainButton('INICIAR', const Color(0xFF43A047), Icons.play_arrow),
        _buildMainButton('DETENER', const Color(0xFFE53935), Icons.stop),
        _buildMainButton('SILENCIAR', const Color(0xFFFFA000), Icons.volume_off),
      ],
    );
  }

  Widget _buildMainButton(String label, Color color, IconData icon) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => widget.onKeyPressed?.call(label),
        borderRadius: BorderRadius.circular(6),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(6),
            border: Border.all(
              color: color.withOpacity(0.7),
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(0.4),
                blurRadius: 4,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: Colors.white, size: 20),
              const SizedBox(height: 2),
              Text(
                label,
                style: const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 8,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
