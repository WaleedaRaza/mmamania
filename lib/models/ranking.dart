import 'fighter.dart';

class Ranking {
  final String id;
  final String weightClass;
  final int position;
  final Fighter fighter;
  final DateTime updatedAt;

  Ranking({
    required this.id,
    required this.weightClass,
    required this.position,
    required this.fighter,
    required this.updatedAt,
  });

  factory Ranking.fromJson(Map<String, dynamic> json) {
    return Ranking(
      id: json['id'] ?? '',
      weightClass: json['weight_class'] ?? '',
      position: json['position'] ?? 0,
      fighter: Fighter.fromJson(json['fighter'] ?? {}),
      updatedAt: DateTime.tryParse(json['updated_at'] ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'weight_class': weightClass,
      'position': position,
      'fighter': fighter.toJson(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  Ranking copyWith({
    String? id,
    String? weightClass,
    int? position,
    Fighter? fighter,
    DateTime? updatedAt,
  }) {
    return Ranking(
      id: id ?? this.id,
      weightClass: weightClass ?? this.weightClass,
      position: position ?? this.position,
      fighter: fighter ?? this.fighter,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  @override
  String toString() {
    return 'Ranking(id: $id, weightClass: $weightClass, position: $position, fighter: ${fighter.name})';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Ranking && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 