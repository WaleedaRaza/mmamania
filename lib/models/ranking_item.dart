import 'fighter.dart';

class RankingItem {
  final String id;
  final String weightClass;
  final int rankPosition;
  final Fighter fighter;
  final bool isChampion;
  final DateTime updatedAt;

  RankingItem({
    required this.id,
    required this.weightClass,
    required this.rankPosition,
    required this.fighter,
    required this.isChampion,
    required this.updatedAt,
  });

  factory RankingItem.fromJson(Map<String, dynamic> json) {
    final fighterData = json['fighters'] as Map<String, dynamic>?;
    final fighter = fighterData != null ? Fighter.fromJson(fighterData) : Fighter.empty();
    
    final rankPosition = json['rank_position'] ?? 0;
    final isChampion = rankPosition == 0;
    
    return RankingItem(
      id: json['id'] ?? '',
      weightClass: json['weight_class'] ?? '',
      rankPosition: rankPosition,
      fighter: fighter,
      isChampion: isChampion,
      updatedAt: DateTime.tryParse(json['updated_at'] ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'weight_class': weightClass,
      'rank_position': rankPosition,
      'fighter': fighter.toJson(),
      'is_champion': isChampion,
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  @override
  String toString() {
    return 'RankingItem(id: $id, weightClass: $weightClass, rankPosition: $rankPosition, fighter: ${fighter.name}, isChampion: $isChampion)';
  }
} 