import 'fighter.dart';

class Ranking {
  final String id;
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
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
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
} 