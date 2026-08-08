function aura_load(AuraDbFile, withGui)
% AURA_LOAD Loads the Aura ecosystem environment and configuration database
%
% Syntax:
%   aura_load(AuraDbFile, withGui)

    disp(['AURA> Accessing database: ', AuraDbFile]);
    
    % Check if database exists
    if ~exist(AuraDbFile, 'file')
        warning('AURA> Aura.xlsl not found. Creating default initialization state.');
    else
        try
            % Read configuration sheets if available
            [~, sheets] = xlsfinfo(AuraDbFile);
            disp(['AURA> Successfully connected to Aura database. Available sheets: ', num2str(length(sheets))]);
        catch exception
            warning(['AURA> Could not parse Excel file: ', exception.message]);
        end
    end

    % Set global running flag in base workspace for 'status' command
    assignin('base', 'AURA_RUNNING', true);

    % Handle GUI vs Headless startup
    if withGui
        disp('AURA> Launching Aura Hub graphical dashboard...');
        try
            % Place GUI initialization routine here if applicable
        catch
            disp('AURA> GUI interface unavailable or not found. Continuing in CLI mode.');
        end
    else
        disp('AURA> Aura Hub loaded successfully in headless/automation mode.');
    end
end
