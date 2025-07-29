import 'fighter.dart';

class Fight {
  final String id;
  final String eventId;
  final String fighter1Id;
  final String fighter2Id;
  final Fighter? fighter1;
  final Fighter? fighter2;
  final DateTime date;
  final String weightClass;
  final int rounds;
  final String? result;
  final String? winnerId;
  final String? method;
  final String? round;
  final String? time;
  final bool isMainEvent;
  final bool isTitleFight;
  final String status;

  Fight({
    required this.id,
    required this.eventId,
    required this.fighter1Id,
    required this.fighter2Id,
    this.fighter1,
    this.fighter2,
    required this.date,
    required this.weightClass,
    required this.rounds,
    this.result,
    this.winnerId,
    this.method,
    this.round,
    this.time,
    this.isMainEvent = false,
    this.isTitleFight = false,
    this.status = 'scheduled',
  });

  factory Fight.fromJson(Map<String, dynamic> json) {
    // Handle result field which might be a JSON object
    String? resultString;
    if (json['result'] != null) {
      if (json['result'] is String) {
        resultString = json['result'];
      } else if (json['result'] is Map<String, dynamic>) {
        // Extract method from result object
        final resultMap = json['result'] as Map<String, dynamic>;
        resultString = resultMap['method']?.toString();
      }
    }
    
    // Handle method field which might be nested in result
    String? methodString;
    if (json['method'] != null) {
      methodString = json['method'].toString();
    } else if (json['result'] is Map<String, dynamic>) {
      final resultMap = json['result'] as Map<String, dynamic>;
      methodString = resultMap['method']?.toString();
    }
    
    // Handle round field which might be nested in result
    String? roundString;
    if (json['round'] != null) {
      roundString = json['round'].toString();
    } else if (json['result'] is Map<String, dynamic>) {
      final resultMap = json['result'] as Map<String, dynamic>;
      roundString = resultMap['round']?.toString();
    }
    
    // Handle time field which might be nested in result
    String? timeString;
    if (json['time'] != null) {
      timeString = json['time'].toString();
    } else if (json['result'] is Map<String, dynamic>) {
      final resultMap = json['result'] as Map<String, dynamic>;
      timeString = resultMap['time']?.toString();
    }
    
    return Fight(
      id: json['id'] ?? '',
      eventId: json['event_id'] ?? '',
      fighter1Id: json['fighter1_id'] ?? '',
      fighter2Id: json['fighter2_id'] ?? '',
      fighter1: json['fighter1'] != null ? Fighter.fromJson(json['fighter1']) : null,
      fighter2: json['fighter2'] != null ? Fighter.fromJson(json['fighter2']) : null,
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
      weightClass: json['weight_class'] ?? '',
      rounds: json['rounds'] ?? 3,
      result: resultString,
      winnerId: json['winner_id']?.toString(),
      method: methodString,
      round: roundString,
      time: timeString,
      isMainEvent: json['is_main_event'] ?? false,
      isTitleFight: json['is_title_fight'] ?? false,
      status: json['status'] ?? 'scheduled',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'event_id': eventId,
      'fighter1_id': fighter1Id,
      'fighter2_id': fighter2Id,
      'fighter1': fighter1?.toJson(),
      'fighter2': fighter2?.toJson(),
      'date': date.toIso8601String(),
      'weight_class': weightClass,
      'rounds': rounds,
      'result': result,
      'winner_id': winnerId,
      'method': method,
      'round': round,
      'time': time,
      'is_main_event': isMainEvent,
      'is_title_fight': isTitleFight,
      'status': status,
    };
  }

  @override
  String toString() {
    return 'Fight(id: $id, fighter1: ${fighter1?.name}, fighter2: ${fighter2?.name}, date: $date, weightClass: $weightClass)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Fight && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 