import 'package:flutter/material.dart';
import '../services/pump_service.dart';
import '../models/pump_model.dart';

/// Pantalla principal - Menú de bombas disponibles
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  final PumpService _pumpService = PumpService();
  List<Pump> _pumps = [];
  bool _isLoading = true;
  
  // Animaciones para las tarjetas
  AnimationController? _animationController;

  @override
  void initState() {
    super.initState();
    _loadPumps();
  }
  
  @override
  void dispose() {
    _animationController?.dispose();
    super.dispose();
  }

  void _setupAnimations() {
    _animationController = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: 300 + (_pumps.length * 100)),
    );
    _animationController!.forward();
  }

  Future<void> _loadPumps() async {
    try {
      final pumps = await _pumpService.getAllPumps();
      setState(() {
        _pumps = pumps;
        _isLoading = false;
      });
      _setupAnimations();
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al cargar bombas: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App Bar con gradiente
          SliverAppBar(
            expandedHeight: 180,
            floating: false,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: const Text(
                'Simulador BIC',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  shadows: [
                    Shadow(
                      color: Colors.black45,
                      blurRadius: 4,
                    ),
                  ],
                ),
              ),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFF0D47A1),
                      Color(0xFF1565C0),
                      Color(0xFF1E88E5),
                    ],
                  ),
                ),
                child: Stack(
                  children: [
                    Positioned(
                      right: -50,
                      top: -30,
                      child: Icon(
                        Icons.medical_services,
                        size: 200,
                        color: Colors.white.withOpacity(0.1),
                      ),
                    ),
                    const Positioned(
                      left: 20,
                      bottom: 60,
                      child: Text(
                        'LANKAMAR',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          letterSpacing: 4,
                          fontWeight: FontWeight.w300,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Botón Escáner
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: _buildScannerButton(),
            ),
          ),

          // Título sección
          const SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                'Bombas Disponibles',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),

          // Lista de bombas
          _isLoading
              ? const SliverFillRemaining(
                  child: Center(child: CircularProgressIndicator()),
                )
              : SliverPadding(
                  padding: const EdgeInsets.all(16),
                  sliver: SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (context, index) => _buildAnimatedPumpCard(_pumps[index], index),
                      childCount: _pumps.length,
                    ),
                  ),
                ),
        ],
      ),
    );
  }

  Widget _buildScannerButton() {
    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF00897B), Color(0xFF26A69A)],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF00897B).withOpacity(0.4),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => Navigator.pushNamed(context, '/scanner'),
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.camera_alt,
                    color: Colors.white,
                    size: 32,
                  ),
                ),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Lankamar Vision',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Escaneá tu bomba con la cámara',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white70,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Tarjeta de bomba con animación staggered
  Widget _buildAnimatedPumpCard(Pump pump, int index) {
    if (_animationController == null) {
      return _buildPumpCard(pump);
    }
    
    // Calcular intervalos para animación escalonada
    final double startInterval = (index * 0.1).clamp(0.0, 0.7);
    final double endInterval = (startInterval + 0.3).clamp(0.0, 1.0);
    
    final animation = CurvedAnimation(
      parent: _animationController!,
      curve: Interval(startInterval, endInterval, curve: Curves.easeOutCubic),
    );
    
    return AnimatedBuilder(
      animation: animation,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, 30 * (1 - animation.value)),
          child: Opacity(
            opacity: animation.value,
            child: child,
          ),
        );
      },
      child: _buildPumpCard(pump),
    );
  }

  Widget _buildPumpCard(Pump pump) {
    // Colores por marca - 7 fabricantes
    Color brandColor;
    IconData brandIcon;
    
    switch (pump.marca.toLowerCase()) {
      case 'baxter':
        brandColor = const Color(0xFF005EB8); // Azul Baxter oficial
        brandIcon = Icons.medical_services;
        break;
      case 'b. braun':
        brandColor = const Color(0xFF009640); // Verde Braun oficial
        brandIcon = Icons.medical_information;
        break;
      case 'innovo':
        brandColor = const Color(0xFF455A64); // Gris azulado
        brandIcon = Icons.medication;
        break;
      case 'mindray':
        brandColor = const Color(0xFF00ACC1); // Cyan moderno
        brandIcon = Icons.monitor_heart;
        break;
      case 'samtronic':
        brandColor = const Color(0xFFEF6C00); // Naranja
        brandIcon = Icons.water_drop;
        break;
      case 'bd':
        brandColor = const Color(0xFF7B1FA2); // Púrpura BD
        brandIcon = Icons.vaccines;
        break;
      case 'fresenius kabi':
        brandColor = const Color(0xFF01579B); // Azul marino Fresenius
        brandIcon = Icons.bloodtype;
        break;
      default:
        brandColor = const Color(0xFF6B7280); // Gris neutro
        brandIcon = Icons.medical_information;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () => _showPumpOptions(pump),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Icono de marca
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: brandColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: brandColor.withOpacity(0.3),
                  ),
                ),
                child: Icon(
                  brandIcon,
                  color: brandColor,
                  size: 32,
                ),
              ),
              const SizedBox(width: 16),
              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: brandColor,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            pump.marca.toUpperCase(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      pump.modelo,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      pump.tipo,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.speed,
                          size: 14,
                          color: Colors.grey[500],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          pump.specsTecnicas.rangoFlujo,
                          style: TextStyle(
                            color: Colors.grey[500],
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }

  void _showPumpOptions(Pump pump) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              pump.nombreCompleto,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: Color(0xFF0D47A1),
                child: Icon(Icons.play_circle, color: Colors.white),
              ),
              title: const Text('Simulador'),
              subtitle: const Text('Practicá con la botonera interactiva'),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushNamed(
                  context,
                  '/simulation',
                  arguments: {'pumpId': pump.id},
                );
              },
            ),
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: Color(0xFFE65100),
                child: Icon(Icons.warning_amber, color: Colors.white),
              ),
              title: const Text('Troubleshooting'),
              subtitle: Text('${pump.erroresYAlarmas.length} errores documentados'),
              onTap: () {
                Navigator.pop(context);
                Navigator.pushNamed(
                  context,
                  '/troubleshooting',
                  arguments: {'pumpId': pump.id},
                );
              },
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
