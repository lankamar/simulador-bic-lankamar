import 'package:flutter/material.dart';

/// Botón primario con gradiente y micro-animaciones
class PrimaryButton extends StatefulWidget {
  final String label;
  final VoidCallback? onPressed;
  final Gradient? gradient;
  final IconData? icon;

  const PrimaryButton({super.key, required this.label, this.onPressed, this.gradient, this.icon});

  @override
  State<PrimaryButton> createState() => _PrimaryButtonState();
}

class _PrimaryButtonState extends State<PrimaryButton> {
  bool _hover = false;
  bool _pressed = false;

  void _setHover(bool v) => setState(() => _hover = v);
  void _setPressed(bool v) => setState(() => _pressed = v);

  @override
  Widget build(BuildContext context) {
    final scale = _pressed ? 0.98 : (_hover ? 1.02 : 1.0);
    final gradient = widget.gradient ??
        const LinearGradient(colors: [Color(0xFF0D47A1), Color(0xFF1976D2)], begin: Alignment.centerLeft, end: Alignment.centerRight);

    return MouseRegion(
      onEnter: (_) => _setHover(true),
      onExit: (_) => _setHover(false),
      child: GestureDetector(
        onTapDown: (_) => _setPressed(true),
        onTapUp: (_) {
          _setPressed(false);
          widget.onPressed?.call();
        },
        onTapCancel: () => _setPressed(false),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          transform: Matrix4.identity()..scale(scale, scale),
          curve: Curves.easeOut,
          decoration: BoxDecoration(
            gradient: gradient,
            borderRadius: BorderRadius.circular(10),
            boxShadow: [
              BoxShadow(color: Colors.black.withOpacity(0.12), blurRadius: _hover ? 10 : 4, offset: const Offset(0, 4)),
            ],
          ),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (widget.icon != null) ...[
                Icon(widget.icon, color: Colors.white, size: 18),
                const SizedBox(width: 8),
              ],
              Text(widget.label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
            ],
          ),
        ),
      ),
    );
  }
}
