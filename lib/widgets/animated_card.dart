import 'package:flutter/material.dart';

/// Tarjeta animada reutilizable:
/// - AnimatedContainer para animación suave de tamaño/sombra
/// - Hero para transición visual al detalle
/// - MouseRegion + GestureDetector para hover / tap micro-animaciones
class AnimatedCard extends StatefulWidget {
  final String heroTag;
  final String title;
  final String subtitle;
  final Gradient gradient;
  final VoidCallback? onTap;

  const AnimatedCard({
    super.key,
    required this.heroTag,
    required this.title,
    this.subtitle = '',
    this.gradient = const LinearGradient(colors: [Colors.blue, Colors.lightBlue]),
    this.onTap,
  });

  @override
  State<AnimatedCard> createState() => _AnimatedCardState();
}

class _AnimatedCardState extends State<AnimatedCard> {
  bool _hover = false;
  bool _pressed = false;

  void _setHover(bool v) => setState(() => _hover = v);
  void _setPressed(bool v) => setState(() => _pressed = v);

  @override
  Widget build(BuildContext context) {
    final double scale = _pressed ? 0.98 : (_hover ? 1.02 : 1.0);
    final double elevation = _hover ? 12 : 6;
    final boxShadow = [
      BoxShadow(
        color: Colors.black.withOpacity(0.12),
        offset: Offset(0, elevation / 4),
        blurRadius: elevation,
      )
    ];

    return MouseRegion(
      onEnter: (_) => _setHover(true),
      onExit: (_) => _setHover(false),
      child: GestureDetector(
        onTapDown: (_) => _setPressed(true),
        onTapUp: (_) {
          _setPressed(false);
          widget.onTap?.call();
        },
        onTapCancel: () => _setPressed(false),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 220),
          transform: Matrix4.identity()..scale(scale, scale),
          curve: Curves.easeOutCubic,
          decoration: BoxDecoration(
            gradient: widget.gradient,
            borderRadius: BorderRadius.circular(12),
            boxShadow: boxShadow,
          ),
          child: Hero(
            tag: widget.heroTag,
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(12),
                splashColor: Colors.white24,
                highlightColor: Colors.white12,
                onTap: widget.onTap,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                  child: Row(
                    children: [
                      // Icono round
                      Container(
                        width: 56,
                        height: 56,
                        decoration: const BoxDecoration(
                          color: Colors.white24,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.medical_services, color: Colors.white),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(widget.title,
                                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 16)),
                            if (widget.subtitle.isNotEmpty)
                              Text(widget.subtitle,
                                  style: const TextStyle(color: Colors.white70, fontSize: 12)),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right, color: Colors.white70),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
