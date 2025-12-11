#!/bin/bash
# TRAINS System Management
# Usage: ./manage_trains.sh [command]

case "$1" in
    stop)
        echo "Stopping all TRAINS modules..."
        pkill -f "python.*(Passenger_UI|Driver_UI|CTC_UI|UI_Structure|main|Test_UI)"
        echo "Done."
        ;;
    status)
        echo "Active TRAINS processes:"
        ps aux | grep -E "python.*(Passenger_UI|Driver_UI|CTC_UI|UI_Structure|main|Test_UI)" | grep -v grep
        ;;
    logs)
        if [ -d "logs" ]; then
            echo "Recent logs:"
            find logs/ -name "*.log" -type f -exec ls -lh {} \; | head -10
            echo ""
            echo "View a log: tail -f logs/FILENAME.log"
        else
            echo "No logs directory."
        fi
        ;;
    help|*)
        echo "TRAINS Management Commands:"
        echo "  ./manage_trains.sh stop    - Stop all modules"
        echo "  ./manage_trains.sh status  - Show running processes"
        echo "  ./manage_trains.sh logs    - List log files"
        ;;
esac
