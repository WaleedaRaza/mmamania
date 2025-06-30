class Fighter {
  final String id;
  final String name;
  final String division;
  final Record record;
  final String? imageUrl;
  final String? status;
  final String? placeOfBirth;
  final String? trainingAt;
  final String? fightingStyle;
  final int? age;
  final double? height;
  final double? weight;
  final String? octagonDebut;
  final double? reach;
  final double? legReach;
  final FighterStats stats;
  final List<FightResult> fightHistory;

  Fighter({
    required this.id,
    required this.name,
    required this.division,
    required this.record,
    this.imageUrl,
    this.status,
    this.placeOfBirth,
    this.trainingAt,
    this.fightingStyle,
    this.age,
    this.height,
    this.weight,
    this.octagonDebut,
    this.reach,
    this.legReach,
    required this.stats,
    required this.fightHistory,
  });

  factory Fighter.fromJson(Map<String, dynamic> json) {
    return Fighter(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      division: json['division'] ?? '',
      record: Record.fromJson(json['record'] ?? {}),
      imageUrl: json['image_url'],
      status: json['status'],
      placeOfBirth: json['place_of_birth'],
      trainingAt: json['training_at'],
      fightingStyle: json['fighting_style'],
      age: json['age'],
      height: _parseDouble(json['height']),
      weight: _parseDouble(json['weight']),
      octagonDebut: json['octagon_debut'],
      reach: _parseDouble(json['reach']),
      legReach: _parseDouble(json['leg_reach']),
      stats: FighterStats.fromJson(json['stats'] ?? {}),
      fightHistory: (json['fight_history'] as List<dynamic>?)
          ?.map((fight) => FightResult.fromJson(fight))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'division': division,
      'record': record.toJson(),
      'image_url': imageUrl,
      'status': status,
      'place_of_birth': placeOfBirth,
      'training_at': trainingAt,
      'fighting_style': fightingStyle,
      'age': age,
      'height': height,
      'weight': weight,
      'octagon_debut': octagonDebut,
      'reach': reach,
      'leg_reach': legReach,
      'stats': stats.toJson(),
      'fight_history': fightHistory.map((fight) => fight.toJson()).toList(),
    };
  }

  String get displayName => name;
  String get recordString => '${record.wins}-${record.losses}-${record.draws}';
  
  @override
  String toString() {
    return 'Fighter(id: $id, name: $name, record: $recordString)';
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Fighter &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  static double? _parseDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) {
      if (value.isEmpty) return null;
      return double.tryParse(value);
    }
    return null;
  }

  factory Fighter.empty() {
    return Fighter(
      id: '',
      name: '',
      division: '',
      record: Record(wins: 0, losses: 0, draws: 0),
      stats: FighterStats(
        fightWinStreak: 0,
        winsByKnockout: 0,
        winsBySubmission: 0,
        strikingAccuracy: 0.0,
        sigStrikesLanded: 0,
        sigStrikesAttempted: 0,
        takedownAccuracy: 0.0,
        takedownsLanded: 0,
        takedownsAttempted: 0,
        sigStrikesLandedPerMin: 0.0,
        sigStrikesAbsorbedPerMin: 0.0,
        takedownAvgPer15Min: 0.0,
        submissionAvgPer15Min: 0.0,
        sigStrikesDefense: 0.0,
        takedownDefense: 0.0,
        knockdownAvg: 0.0,
        averageFightTime: '0:00',
      ),
      fightHistory: [],
    );
  }
}

class Record {
  final int wins;
  final int losses;
  final int draws;

  Record({
    required this.wins,
    required this.losses,
    required this.draws,
  });

  factory Record.fromJson(Map<String, dynamic> json) {
    return Record(
      wins: json['wins'] ?? 0,
      losses: json['losses'] ?? 0,
      draws: json['draws'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'wins': wins,
      'losses': losses,
      'draws': draws,
    };
  }

  String get displayString => '$wins-$losses-$draws';
  int get totalFights => wins + losses + draws;
  double get winPercentage => totalFights > 0 ? (wins / totalFights) * 100 : 0.0;
}

class RankingInfo {
  final String division;
  final int rank;
  final String scrapedAt;

  RankingInfo({
    required this.division,
    required this.rank,
    required this.scrapedAt,
  });

  factory RankingInfo.fromJson(Map<String, dynamic> json) {
    return RankingInfo(
      division: json['division'] ?? '',
      rank: json['rank'] ?? 0,
      scrapedAt: json['scraped_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'division': division,
      'rank': rank,
      'scraped_at': scrapedAt,
    };
  }
}

class FightInfo {
  final String fightId;
  final String opponent;
  final String weightClass;
  final String fightType;
  final String scrapedAt;

  FightInfo({
    required this.fightId,
    required this.opponent,
    required this.weightClass,
    required this.fightType,
    required this.scrapedAt,
  });

  factory FightInfo.fromJson(Map<String, dynamic> json) {
    return FightInfo(
      fightId: json['fight_id'] ?? '',
      opponent: json['opponent'] ?? '',
      weightClass: json['weight_class'] ?? '',
      fightType: json['fight_type'] ?? '',
      scrapedAt: json['scraped_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'fight_id': fightId,
      'opponent': opponent,
      'weight_class': weightClass,
      'fight_type': fightType,
      'scraped_at': scrapedAt,
    };
  }
}

class ResultInfo {
  final String resultId;
  final String opponent;
  final String result;
  final String method;
  final int? round;
  final String weightClass;
  final String scrapedAt;

  ResultInfo({
    required this.resultId,
    required this.opponent,
    required this.result,
    required this.method,
    this.round,
    required this.weightClass,
    required this.scrapedAt,
  });

  factory ResultInfo.fromJson(Map<String, dynamic> json) {
    return ResultInfo(
      resultId: json['result_id'] ?? '',
      opponent: json['opponent'] ?? '',
      result: json['result'] ?? '',
      method: json['method'] ?? '',
      round: json['round'],
      weightClass: json['weight_class'] ?? '',
      scrapedAt: json['scraped_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'result_id': resultId,
      'opponent': opponent,
      'result': result,
      'method': method,
      'round': round,
      'weight_class': weightClass,
      'scraped_at': scrapedAt,
    };
  }

  bool get isWin => result == 'W';
  bool get isLoss => result == 'L';
}

class FighterStats {
  final int fightWinStreak;
  final int winsByKnockout;
  final int winsBySubmission;
  final double strikingAccuracy;
  final int sigStrikesLanded;
  final int sigStrikesAttempted;
  final double takedownAccuracy;
  final int takedownsLanded;
  final int takedownsAttempted;
  final double sigStrikesLandedPerMin;
  final double sigStrikesAbsorbedPerMin;
  final double takedownAvgPer15Min;
  final double submissionAvgPer15Min;
  final double sigStrikesDefense;
  final double takedownDefense;
  final double knockdownAvg;
  final String averageFightTime;

  FighterStats({
    required this.fightWinStreak,
    required this.winsByKnockout,
    required this.winsBySubmission,
    required this.strikingAccuracy,
    required this.sigStrikesLanded,
    required this.sigStrikesAttempted,
    required this.takedownAccuracy,
    required this.takedownsLanded,
    required this.takedownsAttempted,
    required this.sigStrikesLandedPerMin,
    required this.sigStrikesAbsorbedPerMin,
    required this.takedownAvgPer15Min,
    required this.submissionAvgPer15Min,
    required this.sigStrikesDefense,
    required this.takedownDefense,
    required this.knockdownAvg,
    required this.averageFightTime,
  });

  factory FighterStats.fromJson(Map<String, dynamic> json) {
    return FighterStats(
      fightWinStreak: json['fight_win_streak'] ?? 0,
      winsByKnockout: json['wins_by_knockout'] ?? 0,
      winsBySubmission: json['wins_by_submission'] ?? 0,
      strikingAccuracy: (json['striking_accuracy'] ?? 0).toDouble(),
      sigStrikesLanded: json['sig_strikes_landed'] ?? 0,
      sigStrikesAttempted: json['sig_strikes_attempted'] ?? 0,
      takedownAccuracy: (json['takedown_accuracy'] ?? 0).toDouble(),
      takedownsLanded: json['takedowns_landed'] ?? 0,
      takedownsAttempted: json['takedowns_attempted'] ?? 0,
      sigStrikesLandedPerMin: (json['sig_strikes_landed_per_min'] ?? 0).toDouble(),
      sigStrikesAbsorbedPerMin: (json['sig_strikes_absorbed_per_min'] ?? 0).toDouble(),
      takedownAvgPer15Min: (json['takedown_avg_per_15_min'] ?? 0).toDouble(),
      submissionAvgPer15Min: (json['submission_avg_per_15_min'] ?? 0).toDouble(),
      sigStrikesDefense: (json['sig_strikes_defense'] ?? 0).toDouble(),
      takedownDefense: (json['takedown_defense'] ?? 0).toDouble(),
      knockdownAvg: (json['knockdown_avg'] ?? 0).toDouble(),
      averageFightTime: json['average_fight_time'] ?? '0:00',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'fight_win_streak': fightWinStreak,
      'wins_by_knockout': winsByKnockout,
      'wins_by_submission': winsBySubmission,
      'striking_accuracy': strikingAccuracy,
      'sig_strikes_landed': sigStrikesLanded,
      'sig_strikes_attempted': sigStrikesAttempted,
      'takedown_accuracy': takedownAccuracy,
      'takedowns_landed': takedownsLanded,
      'takedowns_attempted': takedownsAttempted,
      'sig_strikes_landed_per_min': sigStrikesLandedPerMin,
      'sig_strikes_absorbed_per_min': sigStrikesAbsorbedPerMin,
      'takedown_avg_per_15_min': takedownAvgPer15Min,
      'submission_avg_per_15_min': submissionAvgPer15Min,
      'sig_strikes_defense': sigStrikesDefense,
      'takedown_defense': takedownDefense,
      'knockdown_avg': knockdownAvg,
      'average_fight_time': averageFightTime,
    };
  }
}

class FightResult {
  final String result; // Win, Loss, Draw
  final String opponent;
  final String event;
  final String date;
  final String round;
  final String time;
  final String method;
  final String? fightCard;

  FightResult({
    required this.result,
    required this.opponent,
    required this.event,
    required this.date,
    required this.round,
    required this.time,
    required this.method,
    this.fightCard,
  });

  factory FightResult.fromJson(Map<String, dynamic> json) {
    return FightResult(
      result: json['result'] ?? '',
      opponent: json['opponent'] ?? '',
      event: json['event'] ?? '',
      date: json['date'] ?? '',
      round: json['round'] ?? '',
      time: json['time'] ?? '',
      method: json['method'] ?? '',
      fightCard: json['fight_card'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'result': result,
      'opponent': opponent,
      'event': event,
      'date': date,
      'round': round,
      'time': time,
      'method': method,
      'fight_card': fightCard,
    };
  }
} 