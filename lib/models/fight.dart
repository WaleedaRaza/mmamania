import 'fighter.dart';

class Fight {
  final String id;
  final String eventId;
  final String? fighter1Id;
  final String? fighter2Id;
  final Fighter? fighter1;
  final Fighter? fighter2;
  // NEW: Direct fighter name fields for the new schema
  final String? fighter1Name;
  final String? fighter2Name;
  // ENHANCED: Winner/Loser fields from new schema
  final String? winnerName;
  final String? loserName;
  final int? fightOrder;
  final bool isMainEvent;
  final bool isCoMainEvent;
  final DateTime date;
  final String weightClass;
  final int rounds;
  final String? result;
  final String? winnerId;
  final String? method;
  final String? round;
  final String? time;
  final bool isTitleFight;
  final String status;
  final Map<String, dynamic>? resultData; // Add this to store the full result object
  final String? notes;

  Fight({
    required this.id,
    required this.eventId,
    this.fighter1Id,
    this.fighter2Id,
    this.fighter1,
    this.fighter2,
    this.fighter1Name, // NEW
    this.fighter2Name, // NEW
    this.winnerName, // ENHANCED
    this.loserName, // ENHANCED
    this.fightOrder, // ENHANCED
    this.isMainEvent = false,
    this.isCoMainEvent = false, // ENHANCED
    required this.date,
    required this.weightClass,
    required this.rounds,
    this.result,
    this.winnerId,
    this.method,
    this.round,
    this.time,
    this.isTitleFight = false,
    this.status = 'scheduled',
    this.resultData,
    this.notes, // ENHANCED
  });

  factory Fight.fromJson(Map<String, dynamic> json) {
    // Handle result field which might be a JSON object
    String? resultString;
    Map<String, dynamic>? resultData;
    String? winnerIdFromResult;
    
    if (json['result'] != null) {
      if (json['result'] is String) {
        resultString = json['result'];
      } else if (json['result'] is Map<String, dynamic>) {
        // Extract data from result object
        final resultMap = json['result'] as Map<String, dynamic>;
        resultString = resultMap['method']?.toString();
        resultData = resultMap;
        winnerIdFromResult = resultMap['winner_id']?.toString(); // ✅ FIXED: Extract winner_id from result
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
    
    // NEW: Handle direct fighter name fields
    final fighter1NameFromJson = json['fighter1_name'] ?? '';
    final fighter2NameFromJson = json['fighter2_name'] ?? '';
    
    // ENHANCED: Handle winner/loser name fields
    final winnerNameFromJson = json['winner_name'] ?? '';
    final loserNameFromJson = json['loser_name'] ?? '';
    final fightOrderFromJson = json['fight_order'];
    
    return Fight(
      id: json['id'] ?? '',
      eventId: json['event_id'] ?? '',
      fighter1Id: json['fighter1_id'] ?? '',
      fighter2Id: json['fighter2_id'] ?? '',
      fighter1: json['fighter1'] != null ? Fighter.fromJson(json['fighter1']) : null,
      fighter2: json['fighter2'] != null ? Fighter.fromJson(json['fighter2']) : null,
      // NEW: Handle direct fighter name fields
      fighter1Name: fighter1NameFromJson,
      fighter2Name: fighter2NameFromJson,
      // ENHANCED: Handle winner/loser name fields
      winnerName: winnerNameFromJson,
      loserName: loserNameFromJson,
      fightOrder: fightOrderFromJson != null ? int.tryParse(fightOrderFromJson.toString()) : null,
      date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
      weightClass: json['weight_class'] ?? '',
      rounds: json['rounds'] ?? 3,
      result: resultString,
      winnerId: winnerIdFromResult ?? json['winner_id']?.toString(), // ✅ FIXED: Use winner_id from result first
      method: methodString,
      round: roundString,
      time: timeString,
      isMainEvent: json['is_main_event'] ?? false,
      isCoMainEvent: json['is_co_main_event'] ?? false, // ENHANCED
      isTitleFight: json['is_title_fight'] ?? false,
      status: json['status'] ?? 'scheduled',
      resultData: resultData,
      notes: json['notes'], // ENHANCED
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
      // NEW: Include direct fighter name fields
      'fighter1_name': fighter1Name,
      'fighter2_name': fighter2Name,
      // ENHANCED: Include winner/loser name fields
      'winner_name': winnerName,
      'loser_name': loserName,
      'fight_order': fightOrder,
      'date': date.toIso8601String(),
      'weight_class': weightClass,
      'rounds': rounds,
      'result': result,
      'winner_id': winnerId,
      'method': method,
      'round': round,
      'time': time,
      'is_main_event': isMainEvent,
      'is_co_main_event': isCoMainEvent, // ENHANCED
      'is_title_fight': isTitleFight,
      'status': status,
      'result_data': resultData,
      'notes': notes, // ENHANCED
    };
  }

  // NEW: Helper method to get fighter name (prioritizes direct name fields)
  String? getFighter1Name() {
    if (fighter1Name != null && fighter1Name!.isNotEmpty) {
      return fighter1Name;
    }
    return fighter1?.name;
  }

  String? getFighter2Name() {
    if (fighter2Name != null && fighter2Name!.isNotEmpty) {
      return fighter2Name;
    }
    return fighter2?.name;
  }

  // ENHANCED: Helper methods for winner/loser names
  String? getWinnerName() {
    if (winnerName != null && winnerName!.isNotEmpty) {
      return winnerName;
    }
    return winner?.name;
  }

  String? getLoserName() {
    if (loserName != null && loserName!.isNotEmpty) {
      return loserName;
    }
    return loser?.name;
  }

  // Helper method to check if a fighter is the winner
  bool isWinner(Fighter fighter) {
    return winnerId == fighter.id;
  }

  // Helper method to check if a fighter is the loser
  bool isLoser(Fighter fighter) {
    return winnerId != null && winnerId != fighter.id;
  }

  // Helper method to get the winner
  Fighter? get winner {
    if (winnerId == null) return null;
    if (winnerId == fighter1?.id) return fighter1;
    if (winnerId == fighter2?.id) return fighter2;
    return null;
  }

  // Helper method to get the loser
  Fighter? get loser {
    if (winnerId == null) return null;
    if (winnerId == fighter1?.id) return fighter2;
    if (winnerId == fighter2?.id) return fighter1;
    return null;
  }

  // ENHANCED: Helper method to get fight display order
  int getDisplayOrder() {
    return fightOrder ?? 1;
  }

  // ENHANCED: Helper method to get fight status display
  String getStatusDisplay() {
    if (winnerName != null && loserName != null) {
      return 'Completed';
    }
    return status;
  }

  // ENHANCED: Helper method to get result display
  String getResultDisplay() {
    if (winnerName != null && loserName != null) {
      return '$winnerName def. $loserName';
    }
    return '${getFighter1Name() ?? 'TBD'} vs ${getFighter2Name() ?? 'TBD'}';
  }

  // ENHANCED: Helper method to get method display
  String getMethodDisplay() {
    if (method != null && method!.isNotEmpty) {
      return method!;
    }
    return 'TBD';
  }

  // ENHANCED: Helper method to get round/time display
  String getRoundTimeDisplay() {
    if (round != null && time != null) {
      return 'R$round $time';
    }
    return '';
  }

  @override
  String toString() {
    return 'Fight(id: $id, winner: ${getWinnerName()}, loser: ${getLoserName()}, order: $fightOrder, date: $date, weightClass: $weightClass)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Fight && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 