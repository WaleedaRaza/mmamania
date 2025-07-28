import 'package:cloud_firestore/cloud_firestore.dart';

class UFCRanking {
  final int rank;
  final String name;
  final String division;
  final String? record;
  final String? url;
  final DateTime lastUpdated;
  final DateTime scrapedAt;

  UFCRanking({
    required this.rank,
    required this.name,
    required this.division,
    this.record,
    this.url,
    required this.lastUpdated,
    required this.scrapedAt,
  });

  factory UFCRanking.fromFirestore(DocumentSnapshot doc) {
    Map<String, dynamic> data = doc.data() as Map<String, dynamic>;
    
    return UFCRanking(
      rank: data['rank'] ?? 0,
      name: data['name'] ?? '',
      division: data['division'] ?? '',
      record: data['record'],
      url: data['url'],
      lastUpdated: (data['last_updated'] as Timestamp).toDate(),
      scrapedAt: (data['scraped_at'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'rank': rank,
      'name': name,
      'division': division,
      'record': record,
      'url': url,
      'last_updated': Timestamp.fromDate(lastUpdated),
      'scraped_at': Timestamp.fromDate(scrapedAt),
    };
  }

  @override
  String toString() {
    return 'UFCRanking(rank: $rank, name: $name, division: $division)';
  }
}

class UFCFighter {
  final String name;
  final String? record;
  final String? division;
  final String? url;
  final String? height;
  final String? weight;
  final String? reach;
  final String? stance;
  final String? dob;
  final String? hometown;
  final String? team;
  final String fighterId;
  final DateTime lastUpdated;
  final DateTime scrapedAt;
  final int? rank;
  final String? rankDivision;
  final String? rankUrl;

  UFCFighter({
    required this.name,
    this.record,
    this.division,
    this.url,
    this.height,
    this.weight,
    this.reach,
    this.stance,
    this.dob,
    this.hometown,
    this.team,
    required this.fighterId,
    required this.lastUpdated,
    required this.scrapedAt,
    this.rank,
    this.rankDivision,
    this.rankUrl,
  });

  factory UFCFighter.fromFirestore(DocumentSnapshot doc) {
    Map<String, dynamic> data = doc.data() as Map<String, dynamic>;
    
    return UFCFighter(
      name: data['name'] ?? '',
      record: data['record'],
      division: data['division'],
      url: data['url'],
      height: data['height'],
      weight: data['weight'],
      reach: data['reach'],
      stance: data['stance'],
      dob: data['dob'],
      hometown: data['hometown'],
      team: data['team'],
      fighterId: data['fighter_id'] ?? '',
      lastUpdated: (data['last_updated'] as Timestamp).toDate(),
      scrapedAt: (data['scraped_at'] as Timestamp).toDate(),
      rank: data['rank'],
      rankDivision: data['rank_division'],
      rankUrl: data['rank_url'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'name': name,
      'record': record,
      'division': division,
      'url': url,
      'height': height,
      'weight': weight,
      'reach': reach,
      'stance': stance,
      'dob': dob,
      'hometown': hometown,
      'team': team,
      'fighter_id': fighterId,
      'last_updated': Timestamp.fromDate(lastUpdated),
      'scraped_at': Timestamp.fromDate(scrapedAt),
      'rank': rank,
      'rank_division': rankDivision,
      'rank_url': rankUrl,
    };
  }

  @override
  String toString() {
    return 'UFCFighter(name: $name, record: $record, division: $division)';
  }
}

class UFCEvent {
  final String title;
  final String? date;
  final String? venue;
  final String? url;
  final List<UFCFight> fights;
  final int totalFights;
  final String eventId;
  final DateTime lastUpdated;
  final DateTime scrapedAt;

  UFCEvent({
    required this.title,
    this.date,
    this.venue,
    this.url,
    required this.fights,
    required this.totalFights,
    required this.eventId,
    required this.lastUpdated,
    required this.scrapedAt,
  });

  factory UFCEvent.fromFirestore(DocumentSnapshot doc) {
    Map<String, dynamic> data = doc.data() as Map<String, dynamic>;
    
    List<UFCFight> fights = [];
    if (data['fights'] != null) {
      fights = (data['fights'] as List)
          .map((fightData) => UFCFight.fromMap(fightData))
          .toList();
    }

    return UFCEvent(
      title: data['title'] ?? '',
      date: data['date'],
      venue: data['venue'],
      url: data['url'],
      fights: fights,
      totalFights: data['total_fights'] ?? 0,
      eventId: data['event_id'] ?? '',
      lastUpdated: (data['last_updated'] as Timestamp).toDate(),
      scrapedAt: (data['scraped_at'] as Timestamp).toDate(),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'title': title,
      'date': date,
      'venue': venue,
      'url': url,
      'fights': fights.map((fight) => fight.toMap()).toList(),
      'total_fights': totalFights,
      'event_id': eventId,
      'last_updated': Timestamp.fromDate(lastUpdated),
      'scraped_at': Timestamp.fromDate(scrapedAt),
    };
  }

  @override
  String toString() {
    return 'UFCEvent(title: $title, totalFights: $totalFights)';
  }
}

class UFCFight {
  final String weightClass;
  final String fighter1;
  final String fighter2;
  final String? winner;
  final String? loser;
  final String? method;
  final String? round;
  final String? time;
  final String? cardType;
  final String? resultType;

  UFCFight({
    required this.weightClass,
    required this.fighter1,
    required this.fighter2,
    this.winner,
    this.loser,
    this.method,
    this.round,
    this.time,
    this.cardType,
    this.resultType,
  });

  factory UFCFight.fromMap(Map<String, dynamic> data) {
    return UFCFight(
      weightClass: data['weight_class'] ?? '',
      fighter1: data['fighter1'] ?? '',
      fighter2: data['fighter2'] ?? '',
      winner: data['winner'],
      loser: data['loser'],
      method: data['method'],
      round: data['round'],
      time: data['time'],
      cardType: data['card_type'],
      resultType: data['result_type'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'weight_class': weightClass,
      'fighter1': fighter1,
      'fighter2': fighter2,
      'winner': winner,
      'loser': loser,
      'method': method,
      'round': round,
      'time': time,
      'card_type': cardType,
      'result_type': resultType,
    };
  }

  @override
  String toString() {
    return 'UFCFight(fighter1: $fighter1 vs fighter2: $fighter2, winner: $winner)';
  }
} 