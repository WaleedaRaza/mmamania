import 'package:json_annotation/json_annotation.dart';

part 'fighter.g.dart';

@JsonSerializable()
class Fighter {
  final String id;
  final String name;
  final String? nickname;
  final String weightClass;
  final Map<String, int> record;
  final double? reach;
  final double? height;
  final String? stance;
  final String? style;
  final Map<String, dynamic> stats;
  final int? ufcRanking;
  final String isActive;
  final DateTime createdAt;
  final DateTime? updatedAt;

  const Fighter({
    required this.id,
    required this.name,
    this.nickname,
    required this.weightClass,
    required this.record,
    this.reach,
    this.height,
    this.stance,
    this.style,
    required this.stats,
    this.ufcRanking,
    required this.isActive,
    required this.createdAt,
    this.updatedAt,
  });

  factory Fighter.fromJson(Map<String, dynamic> json) => _$FighterFromJson(json);
  Map<String, dynamic> toJson() => _$FighterToJson(this);

  Fighter copyWith({
    String? id,
    String? name,
    String? nickname,
    String? weightClass,
    Map<String, int>? record,
    double? reach,
    double? height,
    String? stance,
    String? style,
    Map<String, dynamic>? stats,
    int? ufcRanking,
    String? isActive,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Fighter(
      id: id ?? this.id,
      name: name ?? this.name,
      nickname: nickname ?? this.nickname,
      weightClass: weightClass ?? this.weightClass,
      record: record ?? this.record,
      reach: reach ?? this.reach,
      height: height ?? this.height,
      stance: stance ?? this.stance,
      style: style ?? this.style,
      stats: stats ?? this.stats,
      ufcRanking: ufcRanking ?? this.ufcRanking,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  int get wins => record['wins'] ?? 0;
  int get losses => record['losses'] ?? 0;
  int get draws => record['draws'] ?? 0;
  int get totalFights => wins + losses + draws;
  double get winRate => totalFights > 0 ? wins / totalFights : 0.0;

  String get displayName => nickname != null ? '$name "$nickname"' : name;
  String get recordString => '$wins-$losses${draws > 0 ? '-$draws' : ''}';

  bool get isRanked => ufcRanking != null && ufcRanking! > 0;

  @override
  String toString() {
    return 'Fighter(id: $id, name: $name, record: $recordString)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Fighter && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 