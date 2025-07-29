import 'fighter.dart';

class Ranking {
  final String id;
<<<<<<< HEAD
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
=======
  final String fighterName;
  final String division;
  final int rank;
  final Record record;
  final String? rankChange;
  final String? fighterUrl;
  final bool isChampion;
  final String? fighterId; // Link to detailed fighter profile

  Ranking({
    required this.id,
    required this.fighterName,
    required this.division,
    required this.rank,
    required this.record,
    this.rankChange,
    this.fighterUrl,
    this.isChampion = false,
    this.fighterId,
  });

  factory Ranking.fromJson(Map<String, dynamic> json) {
    final rank = json['rank'] ?? 0;
    final isChampion = rank == 0 || json['is_champion'] == true;
    
    return Ranking(
      id: json['id'] ?? '',
      fighterName: json['fighter_name'] ?? '',
      division: json['division'] ?? '',
      rank: rank,
      record: Record.fromJson(json['record'] ?? {}),
      rankChange: json['rank_change'],
      fighterUrl: json['fighter_url'],
      isChampion: isChampion,
      fighterId: json['fighter_id'] ?? json['fighter_url']?.split('/').last,
>>>>>>> 638a726d2771376ba71e0338bcda2ffc8c49bccd
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
<<<<<<< HEAD
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
=======
      'fighter_name': fighterName,
      'division': division,
      'rank': rank,
      'record': record.toJson(),
      'rank_change': rankChange,
      'fighter_url': fighterUrl,
      'is_champion': isChampion,
      'fighter_id': fighterId,
    };
  }

  // Helper methods
  String get displayRank => isChampion ? 'C' : rank.toString();
  bool get isRanked => !isChampion && rank > 0;
  String get recordString => record.displayString;
>>>>>>> 638a726d2771376ba71e0338bcda2ffc8c49bccd
} 