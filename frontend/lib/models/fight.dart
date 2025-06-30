import 'package:json_annotation/json_annotation.dart';
import 'fighter.dart';

part 'fight.g.dart';

@JsonSerializable()
class Fight {
  final String id;
  final String eventName;
  final DateTime date;
  final String fighterAId;
  final String fighterBId;
  final String weightClass;
  final bool isMainEvent;
  final bool isTitleFight;
  final Map<String, double> odds;
  final String? winnerId;
  final String? method;
  final int? round;
  final String? time;
  final Map<String, dynamic> mlInsights;
  final bool isCompleted;
  final DateTime createdAt;
  final DateTime? updatedAt;
  
  // Related data (not from API)
  final Fighter? fighterA;
  final Fighter? fighterB;
  final Fighter? winner;

  const Fight({
    required this.id,
    required this.eventName,
    required this.date,
    required this.fighterAId,
    required this.fighterBId,
    required this.weightClass,
    required this.isMainEvent,
    required this.isTitleFight,
    required this.odds,
    this.winnerId,
    this.method,
    this.round,
    this.time,
    required this.mlInsights,
    required this.isCompleted,
    required this.createdAt,
    this.updatedAt,
    this.fighterA,
    this.fighterB,
    this.winner,
  });

  factory Fight.fromJson(Map<String, dynamic> json) => _$FightFromJson(json);
  Map<String, dynamic> toJson() => _$FightToJson(this);

  Fight copyWith({
    String? id,
    String? eventName,
    DateTime? date,
    String? fighterAId,
    String? fighterBId,
    String? weightClass,
    bool? isMainEvent,
    bool? isTitleFight,
    Map<String, double>? odds,
    String? winnerId,
    String? method,
    int? round,
    String? time,
    Map<String, dynamic>? mlInsights,
    bool? isCompleted,
    DateTime? createdAt,
    DateTime? updatedAt,
    Fighter? fighterA,
    Fighter? fighterB,
    Fighter? winner,
  }) {
    return Fight(
      id: id ?? this.id,
      eventName: eventName ?? this.eventName,
      date: date ?? this.date,
      fighterAId: fighterAId ?? this.fighterAId,
      fighterBId: fighterBId ?? this.fighterBId,
      weightClass: weightClass ?? this.weightClass,
      isMainEvent: isMainEvent ?? this.isMainEvent,
      isTitleFight: isTitleFight ?? this.isTitleFight,
      odds: odds ?? this.odds,
      winnerId: winnerId ?? this.winnerId,
      method: method ?? this.method,
      round: round ?? this.round,
      time: time ?? this.time,
      mlInsights: mlInsights ?? this.mlInsights,
      isCompleted: isCompleted ?? this.isCompleted,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      fighterA: fighterA ?? this.fighterA,
      fighterB: fighterB ?? this.fighterB,
      winner: winner ?? this.winner,
    );
  }

  bool get isUpcoming => date.isAfter(DateTime.now());
  bool get isPast => date.isBefore(DateTime.now());

  @override
  String toString() {
    return 'Fight(id: $id, eventName: $eventName, date: $date)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Fight && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 