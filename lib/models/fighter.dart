class Fighter {
  final String id;
  final String name;
  final String? nickname;
  final String? weightClass;
  final String? record;
  final String? country;
  final String? team;
  final bool isActive;
  final String? imageUrl;
  final DateTime? lastFightDate;
  final String? lastFightResult;
  final int? ranking;
  final String? rankingWeightClass;

  Fighter({
    required this.id,
    required this.name,
    this.nickname,
    this.weightClass,
    this.record,
    this.country,
    this.team,
    this.isActive = true,
    this.imageUrl,
    this.lastFightDate,
    this.lastFightResult,
    this.ranking,
    this.rankingWeightClass,
  });

  factory Fighter.fromJson(Map<String, dynamic> json) {
    // Handle record field which can be either a JSON object or string
    String? recordString;
    if (json['record'] != null) {
      if (json['record'] is Map<String, dynamic>) {
        // Convert JSON object to string format
        final record = json['record'] as Map<String, dynamic>;
        final wins = record['wins'] ?? 0;
        final losses = record['losses'] ?? 0;
        final draws = record['draws'] ?? 0;
        recordString = '$wins-$losses-$draws';
      } else {
        recordString = json['record'].toString();
      }
    }
    
    return Fighter(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      nickname: json['nickname'],
      weightClass: json['weight_class'],
      record: recordString,
      country: json['country'],
      team: json['team'],
      isActive: json['is_active'] ?? true,
      imageUrl: json['image_url'],
      lastFightDate: json['last_fight_date'] != null 
          ? DateTime.tryParse(json['last_fight_date']) 
          : null,
      lastFightResult: json['last_fight_result'],
      ranking: json['ranking'],
      rankingWeightClass: json['ranking_weight_class'],
    );
  }

  factory Fighter.empty() {
    return Fighter(
      id: '',
      name: 'Unknown Fighter',
      nickname: null,
      weightClass: null,
      record: null,
      country: null,
      team: null,
      isActive: false,
      imageUrl: null,
      lastFightDate: null,
      lastFightResult: null,
      ranking: null,
      rankingWeightClass: null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'nickname': nickname,
      'weight_class': weightClass,
      'record': record,
      'country': country,
      'team': team,
      'is_active': isActive,
      'image_url': imageUrl,
      'last_fight_date': lastFightDate?.toIso8601String(),
      'last_fight_result': lastFightResult,
      'ranking': ranking,
      'ranking_weight_class': rankingWeightClass,
    };
  }

  @override
  String toString() {
    return 'Fighter(id: $id, name: $name, weightClass: $weightClass, record: $record)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Fighter && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 