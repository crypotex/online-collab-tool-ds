package generator;

import org.yakindu.sct.model.sexec.ExecutionFlow;
import org.yakindu.sct.model.sexec.ExecutionState;
import org.yakindu.sct.model.sgen.GeneratorEntry;
import org.yakindu.sct.generator.core.IExecutionFlowGenerator;
import org.eclipse.xtext.generator.IFileSystemAccess;

public class gn implements IExecutionFlowGenerator{
	private static final String LBR = "\n\r";

	public void generate(ExecutionFlow flow, GeneratorEntry entry, IFileSystemAccess fsa) {
		StringBuilder builder = new StringBuilder();
		builder.append("The name of the state machine is ");
		builder.append(flow.getName());
		builder.append(LBR).append(LBR);
		builder.append("The state machine has the following states:");
		builder.append(LBR).append(LBR);
		for (ExecutionState state : flow.getStates()) {
			builder.append(
					state.getName().replaceFirst(flow.getName() + "\\.", ""))
					.append(LBR);
		}
		fsa.generateFile(flow.getName() + ".txt", builder.toString());
	}
}
