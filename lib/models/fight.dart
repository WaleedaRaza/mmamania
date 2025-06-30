import 'fighter.dart';

class Fight {
  final String id;
  final Fighter fighter1;
  final Fighter fighter2;
  final String weightClass;
  final String fightType;
  final String? eventId;
  final DateTime date;
  final String? winner;
  final String? method;
  final int? round;
  final String? time;

  Fight({
    required this.id,
    required this.fighter1,
    required this.fighter2,
    required this.weightClass,
    required this.fightType,
    this.eventId,
    required this.date,
    this.winner,
    this.method,
    this.round,
    this.time,
  });

  factory Fight.fromJson(Map<String, dynamic> json) {
    return Fight(
      id: json['id'] ?? '',
      fighter1: Fighter.fromJson(json['fighter1'] ?? {}),
      fighter2: Fighter.fromJson(json['fighter2'] ?? {}),
      weightClass: json['weight_class'] ?? '',
      fightType: json['fight_type'] ?? '',
      eventId: json['event_id'],
      date: json['date'] != null ? DateTime.parse(json['date']) : DateTime.now(),
      winner: json['winner'],
      method: json['method'],
      round: json['round'],
      time: json['time'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'fighter1': fighter1.toJson(),
      'fighter2': fighter2.toJson(),
      'weight_class': weightClass,
      'fight_type': fightType,
      'event_id': eventId,
      'date': date.toIso8601String(),
      'winner': winner,
      'method': method,
      'round': round,
      'time': time,
    };
  }

  String get displayTitle => '${fighter1.name} vs ${fighter2.name}';
  bool get isCompleted => winner != null;
  bool get isUpcoming => !isCompleted;
  
  Fighter? get winnerFighter {
    if (winner == 'fighter1') return fighter1;
    if (winner == 'fighter2') return fighter2;
    return null;
  }
  
  Fighter? get loserFighter {
    if (winner == 'fighter1') return fighter2;
    if (winner == 'fighter2') return fighter1;
    return null;
  }
} 